import numpy as np
from deva import elicit, fileio

import random


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


class DummyEliciter(BoundsEliciter):
    """Dummy Eliciter that selects random candidates"""

    def __init__(self, ref, table, sign, attribs, steps):
        # assert candidates, "No candidate models"
        # BoundsEliciter.__init__(self)
        # self.candidates = list(candidates)
        # candidates

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
        w /= (w@w)**.5  # normalise
        self.w = w

        dims = len(self.ref)

        # TODO: random choice
        # rand_candidate = random.choice(self.candidates)
        # if len(self.candidates) > 1:
        #     self._query = elicit.Pair("baseline", rand_candidate)
        # else:
        #     self._query = None

        # TODO random candidate choice ,choice = query
        
        choice = np.zeros(dims, float) - 1
        while (choice < 0).any():
            diff = np.random.randn(len(self.ref)) * self.radius
            diff -= w * (diff @ w) / (w @ w)  # make perpendicular
            diff /= np.sum((diff/self.radius)**2) ** .5  # re-normalise
            choice = self.ref + diff

        self.choice = choice  # candidate

        self.query = elicit.Candidate(
            fileio.autoname(self._step),
            dict(zip(self.attribs, choice))
        )
        self._step += 1
        # return

    def guess(self, q):
        return ((q - self.ref) @ self.w < 0)

    @property
    def terminated(self):
        return self._step > self.steps

    # @property
    # def result(self):
    #     assert self._step > self.steps, "Not terminated."
    #     return  # TODO


class TestSampler(BoundsEliciter):
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
