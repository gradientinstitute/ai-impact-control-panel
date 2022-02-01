import numpy as np
from deva import elicit, fileio

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier


# Things to try:
# TODO: limit query perturbations to 2 dimensions
# TODO: provide a tunable exploration/exploitation balance
# TODO: ensure graceful handling of hard bounds (eg 100%)
# TODO: elicit the reference point as well as gradients
# TODO: elicit non-linear boundaries (provided client can receive them)

class BoundsEliciter:
    '''Base class for bounds elicitation'''

    # Just a promise that inheriting classes will have these members
    def observe(self, label):
        raise NotImplementedError

    def guess(self, q):
        raise NotImplementedError

    def check_valid(self, q):
        """Determine whether a query is valid."""
        # could be something like (choice < 0).any():
        return True  # placeholder

    def predict_prob(self, n_samples):
        raise NotImplementedError

    @property
    def terminated(self):
        raise NotImplementedError


class KNeighborsEliciter(BoundsEliciter):
    """
    A model making non-linear assumption.
    Eliciter using KNeighborsRegressor
    which helps to generate the candidate in the query closer
    to the boundary in order to narrow the error.
    """

    def __init__(self, ref, table, attribs, steps):
        """
        Parameters
        ----------
            ref: array
                an array representing the reference system (1 * m metrics)
            table: array
                a 2d array storing all the candidates
                (n candidates * m metrics)
            attribs: array
                metrics for each candidate
            steps: int
                decides when to terminate
        """
        self.attribs = attribs
        radius = 0.5 * table.std(axis=0)  # scale of perturbations
        ref = np.asarray(ref, dtype=float)  # sometimes autocasts to long int
        radius = np.asarray(radius, dtype=float)

        self.ref = ref
        self.radius = radius
        self._step = 0
        self.steps = steps
        self._converge = 0  # No. of steps when the model starts to be stable

        self.neigh = KNeighborsClassifier(n_neighbors=5)

        # Initialise
        X = [[10, 0], [20, 0], [150, 0], [0, 10],
             [0, 20], [0, 150], [100, 100]]
        y = [1, 1, 0, 1, 1, 0, 0]
        self.X = X
        self.y = y

        self.neigh.fit(self.X, self.y)

        self._update()

    # input
    def observe(self, label):
        self.X.append(self.choice)
        self.y.append(label)

        self.neigh.fit(self.X, self.y)

        self._update()

    def _update(self):
        # make random candidates
        def random_choice(n):
            choices = []
            for _ in range(n):
                while True:
                    choice = np.random.rand(len(self.ref)) * 100
                    choices.append(choice)
                    if self.check_valid(choice):
                        break
            return choices

        # KNeighborsRegressor
        test_X = random_choice(1000)

        # finding the least confident candidate
        probabilities = self.neigh.predict_proba(test_X)[:, 1]
        min_index = np.argmin(np.abs(probabilities - 0.5))

        self.choice = test_X[min_index]

        self.query = elicit.Candidate(
            fileio.autoname(self._step),
            dict(zip(self.attribs, self.choice))
        )
        self._step += 1

        return

    def guess(self, q):
        r = 10
        return np.logical_and((np.array(distance(q, self.ref)) >= r),
                              is_below(q, self.ref))

    @property
    def terminated(self):
        return self._step > self.steps

    def predict_prob(self, test_samp):
        probabilities = self.neigh.predict_proba(test_samp)
        return probabilities


class LinearActive(BoundsEliciter):
    """
    Eliciter using Logistics Regression
    which helps to generate the candidate in the query closer
    to the boundary in order to narrow the error.
    """

    def __init__(self, ref, table, attribs,
                 steps, epsilon, n_steps_converge):
        """
        Parameters
        ----------
            ref: array
                an array representing the reference system (1 * m metrics)
            table: array
                a 2d array storing all the candidates
                (n candidates * m metrics)
            attribs: array
                metrics for each candidate
            steps: int
                decides when to terminate
            epsilon: float
                the difference of the current weight and the weight
                from the previous step to determine when to terminate
            n_steps_converge: int
                the number of steps that shows the model converges
        """
        self.attribs = attribs
        radius = 0.5 * table.std(axis=0)  # scale of perturbations
        ref = np.asarray(ref, dtype=float)  # sometimes autocasts to long int
        radius = np.asarray(radius, dtype=float)

        self.ref = ref
        self.radius = radius
        self._step = 0
        self.steps = steps
        self.epsilon = epsilon
        self._converge = 0  # No. of steps when the model starts to be stable
        self.n_steps_converge = n_steps_converge

        self.old_w = 0

        self.lr = LogisticRegression()  # Create a logistic regression instance

        # Initialise
        X = [ref+radius, ref-radius]
        y = [0, 1]
        self.X = X
        self.y = y

        self.lr.fit(self.X, self.y)

        self._update()
        self.baseline = elicit.Candidate("baseline", dict(zip(attribs, ref)))

    # input
    def observe(self, label):
        self.X.append(self.choice)
        self.y.append(label)

        self.lr.fit(self.X, self.y)

        self._update()

    def _update(self):
        self.w = self.lr.coef_[0]

        w_diff = np.abs(self.w - self.old_w)
        self.sum_diff_w = np.sum(w_diff)

        self.old_w = self.w.copy()

        # Helper function: make random candidate
        def random_choice(n):
            choices = []
            for _ in range(n):
                while True:
                    diff = np.random.randn(len(self.ref)) * self.radius
                    choice = self.ref + diff
                    choices.append(choice)
                    if self.check_valid(choice):
                        break
            return choices

        # logistic regressor
        test_X = random_choice(1000)

        # finding the least confident candidate
        probabilities = self.lr.predict_proba(test_X)[:, 1]
        min_index = np.argmin(np.abs(probabilities - 0.5))

        self.choice = test_X[min_index]

        self.query = elicit.Candidate(
            fileio.autoname(self._step),
            dict(zip(self.attribs, self.choice))
        )
        self._step += 1

        # count the number of steps when the model becomes stable
        if self.sum_diff_w <= self.epsilon:
            self._converge += 1
        else:
            self._converge = 0

        return

    def guess(self, q):
        return ((q - self.ref) @ self.w < 0)

    @property
    def terminated(self):
        # either the steps reach the limit or the model converges
        return (self._step > self.steps or
                (self.sum_diff_w <= self.epsilon and
                 self._converge >= self.n_steps_converge))

    def predict_prob(self, test_samp):
        probabilities = self.lr.predict_proba(test_samp)
        return probabilities


class LinearRandom(BoundsEliciter):
    """
    LinearRandom Eliciter that selects random candidates
    and asks whether the user prefer candidate to baseline or not.
    The bound generated separates the candidates being accepted and
    those being rejected.
    """

    def __init__(self, ref, table, attribs, steps):
        """
        Parameters
        ----------
            ref: array
                an array representing the reference system (1 * m metrics)
            table: array
                a 2d array storing all the candidates
                (n candidates * m metrics)
            attribs: array
                metrics for each candidate
            steps: int
                decides when to terminate
        """

        self.attribs = attribs
        radius = 0.5 * table.std(axis=0)  # scale of perturbations
        ref = np.asarray(ref, dtype=float)  # sometimes autocasts to long int
        radius = np.asarray(radius, dtype=float)

        self.ref = ref
        self.radius = radius
        self._step = 0
        self.steps = steps

        self.lr = LogisticRegression()  # Create a logistic regression instance

        # Initialise
        X = [ref+radius, ref-radius]
        y = [0, 1]
        self.X = X
        self.y = y
        self.lr.fit(self.X, self.y)

        self._update()

        self.baseline = elicit.Candidate("baseline", dict(zip(attribs, ref)))

    def observe(self, label):
        self.X.append(self.choice)
        self.y.append(label)

        self.lr.fit(self.X, self.y)

        self._update()

    def _update(self):
        self.w = self.lr.coef_[0]

        while True:
            diff = np.random.randn(len(self.ref)) * self.radius
            choice = self.ref + diff
            if self.check_valid(choice):
                break

        self.choice = choice  # candidate

        self.query = elicit.Candidate(
            fileio.autoname(self._step),
            dict(zip(self.attribs, choice))
        )
        self._step += 1
        return

    def guess(self, q):
        return ((q - self.ref) @ self.w < 0)

    @property
    def terminated(self):
        return self._step > self.steps

    def predict_prob(self, test_samp):
        probabilities = self.lr.predict_proba(test_samp)

        return probabilities


class PlaneSampler(BoundsEliciter):
    """Example of a basic sampler that elicits a boundary hyperplane."""

    def __init__(self, ref, table, attribs, steps):
        self.attribs = attribs
        radius = 0.5 * table.std(axis=0)  # scale of perturbations
        ref = np.asarray(ref, dtype=float)  # sometimes autocasts to long int
        radius = np.asarray(radius, dtype=float)

        self.ref = ref
        self.radius = radius
        dims = len(ref)
        self._step = 0
        self.steps = steps

        # Initialise
        X = [ref+radius]
        for d in range(dims):
            v = ref + 0
            # these labels are virtual / allowed to go negative
            v[d] += radius[d]  # adding radius makes it better
            X.append(v)
        self.X = X
        self._update()
        self.baseline = elicit.Candidate("baseline", dict(zip(attribs, ref)))

    def observe(self, label):
        # if ref+a is a no, ref-a is a yes
        if label:
            self.X.append(2.*self.ref-self.choice)
        else:
            self.X.append(self.choice)
        self._update()

    def _update(self):
        # linear discriminant analysis gives a decision plane normal
        diff = np.array(self.X, dtype=float) - self.ref[None, :]
        dcov = np.cov(diff.T)
        dmean = diff.mean(axis=0)
        w = np.linalg.solve(dcov, dmean)
        w /= (w@w)**.5  # normalise
        self.w = w

        dims = len(self.ref)
        choice = np.zeros(dims, float) - 1
        while True:
            diff = np.random.randn(len(self.ref)) * self.radius
            diff -= w * (diff @ w) / (w @ w)  # make perpendicular
            diff /= np.sum((diff/self.radius)**2) ** .5  # re-normalise
            choice = self.ref + diff
            if self.check_valid(choice):
                break

        self.choice = choice
        self.query = elicit.Candidate(
            fileio.autoname(self._step),
            dict(zip(self.attribs, choice))
        )
        self._step += 1
        return

    def guess(self, q):
        return ((q - self.ref) @ self.w < 0)

    @property
    def terminated(self):
        return self._step > self.steps

    def predict_prob(self, test_samp):
        probabilities = [0.5] * len(test_samp)
        return probabilities


def tabulate(candidates, metrics):
    """Convert candidates to a table of attributes."""
    attribs = sorted(candidates[0].attributes)
    table = np.zeros((len(candidates), len(attribs)))
    for i, c in enumerate(candidates):
        table[i, :] = [c[a] for a in attribs]

    return attribs, table


def distance(a, center):
    a = np.array(a)
    center = np.array(center)
    dist = np.sqrt(np.sum((a - center) ** 2, axis=-1))
    return dist


def is_below(q, center):
    # Check whether a point is below a straight line through the center
    q = np.array(q)
    if q.ndim == 1:
        x = q[0]
        y = q[1]
    else:
        x = q[:, 0]
        y = q[:, 1]
    b = np.sum(center)
    y_max = -x + b

    return y <= y_max
