import numpy as np
from functools import partial
from deva import halfspace


class Candidate:
    def __init__(self, name, attributes, spec_name):
        self.name = name
        self.attributes = attributes
        self.spec_name = spec_name

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

    def __init__(self, candidates, scenario):
        assert candidates, "No candidate models"
        Eliciter.__init__(self)
        self.candidates = list(candidates)  # copy references
        self._update()

    def input(self, choice):
        assert self._query and choice in self._query, "Response mismatch."
        if choice == self.query[1].name:
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
    _active_kw = {'query_order': halfspace.rank_compar_ord}

    def __init__(self, candidates, scenario):
        if len(candidates) < 2:
            raise RuntimeError('Two or more candidates required.')
        Eliciter.__init__(self)
        self.candidates = list(candidates)
        attribs = list(candidates[0].attributes.keys())
        self._result = None

        # convert data structures to a numpy array
        data = []
        for c in candidates:
            data.append([c[a] for a in attribs])

        metrics = scenario['metrics']
        signs = [1 if metrics[a]['higherIsBetter'] else -1 for a in attribs]
        data = np.array(data) * np.array(signs)

        self.active = self._active_alg(
            data,
            yield_indices=True,
            **self._active_kw
        )
        self._update()

    def input(self, choice):
        assert self._query and choice in self._query, "Response mismatch."
        if choice == self._query[0].name:
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
            ind = res if np.issubdtype(type(res), np.int64) else res[-1]
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
    _active_kw = {'query_order': halfspace.max_compar_rand}


class ActiveMaxSmooth(ActiveRanking):

    _active_alg = halfspace.HalfspaceMax
    _active_kw = {'query_order': halfspace.max_compar_smooth}


class ActiveMaxPrimary(ActiveRanking):

    _active_alg = halfspace.HalfspaceMax

    def __init__(self, candidates, scenario):
        if 'primary_metric' not in scenario:
            raise RuntimeError('Expecting a primary_metric to be specified in'
                               ' the metadata.')
        pmetric = scenario['primary_metric']
        attribs = list(candidates[0].attributes.keys())
        pri_ind = attribs.index(pmetric)
        qorder = partial(halfspace.max_compar_primary, primary_index=pri_ind)
        self._active_kw = {'query_order': qorder}
        super().__init__(candidates, scenario)
