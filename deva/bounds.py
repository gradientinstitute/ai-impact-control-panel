import numpy as np
from deva import elicit, fileio

from sklearn.linear_model import LogisticRegression


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

    @property
    def terminated(self):
        raise NotImplementedError


class LinearActive(BoundsEliciter):
    """
    Eliciter using Logistics Regression
    which helps to generate the candidate in the query closer
    to the boundary in order to narrow the error.
    """

    def __init__(self, ref, table, sign, attribs,
                 steps, epsilon, n_steps_converge):
        """
        Parameters
        ----------
            ref: array
                an array representing the reference system (1 * m metrics)
            table: array
                a 2d array storing all the candidates
                (n candidates * m metrics)
            sign: int
                helps to always minimise/maximise the values
                in different metrics
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
        radius = np.asarray(radius, dtype=float) * np.asarray(sign)

        # NOTE: "higherisbetter" is encoded in sign of radius
        self.ref = ref
        self.radius = radius
        dims = len(ref)
        self._step = 0
        self.steps = steps
        self.epsilon = epsilon
        self._converge = 0  # No. of steps when the model starts to be stable
        self.n_steps_converge = n_steps_converge

        self.old_w = 0

        self.lr = LogisticRegression()  # Create a logistic regression instance

        # Initialise
        X = [ref+radius]
        y = [1]
        for d in range(dims):
            v = ref + 0
            # these labels are virtual / allowed to go negative
            v[d] += radius[d]  # adding radius makes it better
            X.append(v)
            y.append(1)
        self.X = X
        self.y = y

        self.baseline = elicit.Candidate("baseline", dict(zip(attribs, ref)))

        self._update()

    # input
    def observe(self, label):
        # if ref+a is a no, ref-a is a yes
        if label:
            self.X.append(2.*self.ref-self.choice)
        else:
            self.X.append(self.choice)
        self.y.append(label)

        # If there is more than one class
        if 0 in self.y:
            self.lr.fit(self.X, self.y)

        self._update()

    def _update(self):
        # linear discriminant analysis gives a decision plane normal
        diff = np.array(self.X, dtype=float) - self.ref[None, :]
        dcov = np.cov(diff.T)
        dmean = diff.mean(axis=0)
        w = np.linalg.solve(dcov, dmean)
        w /= (w@w)**.5  # normalise
        self.w = w

        w_diff = abs(self.w - self.old_w)
        self.sum_diff_w = sum(w_diff)

        if self.steps > 0:
            self.old_w = self.w.copy()

        dims = len(self.ref)

        # Helper function: make random candidate
        def random_choice():
            choice = np.zeros(dims, float) - 1
            while (choice < 0).any():
                diff = np.random.randn(len(self.ref)) * self.radius
                diff -= w * (diff @ w) / (w @ w)  # make perpendicular
                diff /= np.sum((diff/self.radius)**2) ** .5  # re-normalise
                choice = self.ref + diff
            return choice

        # logistic regressor
        if 0 in self.y:  # If a logistic regression model exists
            test_X = [random_choice() for i in range(1000)]

            # finding the least confident candidate
            probabilities = self.lr.predict_proba(test_X)[:, 1]
            min_index = np.argmin(abs(probabilities - 0.5))

            self.choice = test_X[min_index]

        # if there is no logreg model, do random choice
        else:
            self.choice = random_choice()

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
        if self._step > self.steps:
            print("Teminated: max steps are reached")
            return self._step > self.steps
        else:
            print("Terminated: model converges")
            return (self.sum_diff_w <= 0.1 and
                    self._converge >= self.n_steps_converge)


class LinearRandom(BoundsEliciter):
    """
    LinearRandom Eliciter that selects random candidates
    and asks whether the user prefer candidate to baseline or not.
    The bound generated separates the candidates being accepted and
    those being rejected.
    """

    def __init__(self, ref, table, sign, attribs, steps):
        """
        Parameters
        ----------
            ref: array
                an array representing the reference system (1 * m metrics)
            table: array
                a 2d array storing all the candidates
                (n candidates * m metrics)
            sign: int
                helps to always minimise/maximise the values
                in different metrics
            attribs: array
                metrics for each candidate
            steps: int
                decides when to terminate
        """

        self.attribs = attribs
        radius = 0.5 * table.std(axis=0)  # scale of perturbations
        ref = np.asarray(ref, dtype=float)  # sometimes autocasts to long int
        radius = np.asarray(radius, dtype=float) * np.asarray(sign)

        # NOTE: "higherisbetter" is encoded in sign of radius
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

    # input
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
        self.w = w

        dims = len(self.ref)

        # random candidate choice
        choice = np.zeros(dims, float) - 1
        while (choice < 0).any():
            diff = np.random.randn(len(self.ref)) * self.radius
            choice = self.ref + diff

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


class PlaneSampler(BoundsEliciter):
    """Example of a basic sampler that elicits a boundary hyperplane."""

    def __init__(self, ref, table, sign, attribs, steps):
        self.attribs = attribs
        radius = 0.5 * table.std(axis=0)  # scale of perturbations
        ref = np.asarray(ref, dtype=float)  # sometimes autocasts to long int
        radius = np.asarray(radius, dtype=float) * np.asarray(sign)

        # NOTE: "higherisbetter" is encoded in sign of radius
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
        while (choice < 0).any():
            diff = np.random.randn(len(self.ref)) * self.radius
            diff -= w * (diff @ w) / (w @ w)  # make perpendicular
            diff /= np.sum((diff/self.radius)**2) ** .5  # re-normalise
            choice = self.ref + diff
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


def tabulate(candidates, metrics):
    """Convert object candidates and higherIsBetter to arrays."""
    attribs = sorted(candidates[0].attributes)
    table = np.zeros((len(candidates), len(attribs)))
    for i, c in enumerate(candidates):
        table[i, :] = [c[a] for a in attribs]

    sign = np.array([-1 if metrics[a]["higherIsBetter"] else 1
                     for a in attribs])

    return attribs, table, sign
