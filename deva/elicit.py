from deva import halfspace
import numpy as np


class Candidate:
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

    def __getitem__(self, key):
        return self.attributes[key]

    def __repr__(self):
        return f"Candidate({self.name})"


class Pair(tuple):
    def __new__(self, a: Candidate, b: Candidate):
        assert isinstance(a, Candidate) and isinstance(b, Candidate)
        return tuple.__new__(self, (a, b))

    def __contains__(self, x):
        return ((x == self[0].name) or (x == self[1].name)
                or tuple.__contains__(self, x))

    def __repr__(self):
        return f"Pair({self[0].name}, {self[1].name})"



class Eliciter:
    '''Base class for elicitation algorithms.'''

    # Just a promise that inheriting classes will have these members
    def terminated(self, choice):
        raise NotImplementedError

    @property
    def query(self, choice):
        raise NotImplementedError

    @property
    def result(self, choice):
        raise NotImplementedError

    def input(self, choice):
        raise NotImplementedError


class Toy(Eliciter):
    '''Simple eliciter with sequential elimination.'''

    def __init__(self, candidates):
        assert candidates, "No candidate models"
        Eliciter.__init__(self)
        self.candidates = list(candidates)  # copy references
        self._update()

    def input(self, choice):
        assert self._query and choice in self._query, "Response mismatch."
        if choice==self.query[1].name:
            self.candidates.remove(self.query[0])
        else:
            self.candidates.remove(self.query[1])
        self._update()

    @property
    def terminated(self):
        return len(self.candidates) == 1

    @property
    def result(self):
        assert len(self.candidates) == 1, "Not terminated."
        return self.candidates[0]

    @property
    def query(self):
        return self._query

    def _update(self):
        if len(self.candidates) > 1:
            self._query = Pair(self.candidates[0], self.candidates[1])
        else:
            self._query = None


# Eliciter implementations
class ActiveRanking(Eliciter):

    _active_alg = halfspace.HalfspaceRanking

    def __init__(self, candidates):
        assert candidates, "No candidate models"
        Eliciter.__init__(self)
        self.candidates = list(candidates)
        attribs = list(candidates[0].attributes.keys())
        self._result = None

        # convert data structures to a numpy array
        data = []
        for c in candidates:
            data.append([c[a] for a in attribs])

        self.active = self._active_alg(np.array(data), True)
        self._update()

    def input(self, choice):
        assert self._query and choice in self._query, "Response mismatch."
        if choice==self._query[0].name:
            val = 1
        else:
            val = -1
        self.active.put_response(val)
        self._update()

    def _update(self):
        if self.active.next_round():
            a, b = self.active.get_query()
            self._query = Pair(self.candidates[a], self.candidates[b])
        else:
            res = self.active.get_result()
            ind = res if isinstance(res, int) else res[-1]
            self._result = self.candidates[ind]
            self._query = None

    @property
    def result(self):
        return self._result

    @property
    def query(self):
        return self._query

    @property
    def terminated(self):
        return self._result is not None


class ActiveMax(ActiveRanking):

    _active_alg = halfspace.HalfspaceMax
