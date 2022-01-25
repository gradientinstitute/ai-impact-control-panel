"""Preference eliciter module."""
from itertools import combinations
from functools import partial
import numpy as np
from deva import halfspace


class Candidate:
    def __init__(self, name, attributes, spec_name=None):
        self.name = name
        self.attributes = attributes
        self.spec_name = spec_name or name

    def __getitem__(self, key):
        return self.attributes[key]

    def __repr__(self):
        return f"Candidate({self.name})"

    def get_attr(self):
        return self.attributes.values()


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

    @staticmethod
    def description():
        # placeholder for the description of eliciter
        raise NotImplementedError


class VotingEliciter(Eliciter):
    '''Simple eliciter that chooses the most selected candidate'''

    def __init__(self, candidates, scenario):
        assert candidates, "No candidate models"
        Eliciter.__init__(self)
        self.candidates = list(candidates)  # copy references
        # save the number of time each candidate is chosen
        self.chosen = dict.fromkeys(self.candidates, 0)
        self.i = 0  # increasing index
        # all the possible query pairs
        self.comparisons = list(combinations(self.candidates, 2))

        self._update()

    def input(self, choice):
        if choice == self.query[0].name:
            self.chosen[self.query[0]] += 1
        if choice == self.query[1].name:
            self.chosen[self.query[1]] += 1

        self._update()

    @property
    def terminated(self):
        return self.i == len(self.comparisons)

    @property
    def result(self):
        assert self.i == len(self.comparisons), "Not terminated"
        return max(self.candidates, key=self.chosen.get)

    @property
    def query(self):
        return self._query

    def _update(self):
        if len(self.comparisons) >= 1 and self.i < len(self.comparisons):
            queries = self.comparisons[self.i]
            self._query = (queries[0], queries[1])
            self.i += 1
        else:
            self._query = None

    @staticmethod
    def description():
        return "VotingEliciter Description"


class Toy(Eliciter):
    '''Simple eliciter with sequential elimination.'''

    def __init__(self, candidates, scenario):
        assert candidates, "No candidate models"
        Eliciter.__init__(self)
        self.candidates = list(candidates)  # copy references
        self._update()

    def input(self, choice):
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
            self._query = (self.candidates[0], self.candidates[1])
        else:
            self._query = None

    @staticmethod
    def description():
        return "Toy description"


class Enautilus(Eliciter):
    '''Enautilus Eliciter from paper
       E-NAUTILUS: A decision support system for complex multiobjective
       optimization problems based on the NAUTILUS method'''
    _nadir = {}
    _ideal = {}
    _h = 3
    _ns = 2

    def __init__(self, candidates, scenario):
        '''Initialise the eliciter, generate initial ideal point and
           ndair point from the given candidates, and extract attributes
           of the candidates'''
        if len(candidates) < 2:
            raise RuntimeError('Two or more candidates required.')
        Eliciter.__init__(self)
        self.candidates = list(candidates)
        self.attribs = list(candidates[0].attributes.keys())
        # calculate ideal and nadir
        for att in self.attribs:
            min = None
            max = None
            for candidate in candidates:
                temp = candidate.attributes[att]
                if min is None or temp < min:
                    min = temp
                if max is None or temp > max:
                    max = temp
            self._ideal[att] = min
            self._nadir[att] = max
        self._update()

    def get_z_points(self):
        '''Return ideal point and nadir point in a list'''
        return [self._ideal, self._nadir]

    def updateForN(self, n1, ns):
        '''Update the number of questions
        and options the user would like to have'''
        self._h = n1 + 1
        self._ns = ns
        self._update()

    @property
    def query(self):
        '''Return the current query'''
        return self._query

    @property
    def terminated(self):
        '''Check if the termination condition is met'''
        return (self._h <= 0) or (len(self.candidates) == 1)

    @property
    def result(self):
        '''Return result of the eliciter if the termination condition is met'''
        assert (self._h <= 0) or (len(self.candidates) == 1), "Not terminated."
        X = []
        for can in self.candidates:
            X.append(np.array(list(can.get_attr())))
        return self.candidates[np.linalg.norm(np.array(X) - np.array(list(
                                            self._nadir.values()))).argmin()]

    def input(self, choice):
        '''Receive input from the user and update new
         ideal point, nadir point, and remaining candidates'''
        choice = self._query[int(choice)]
        self._nadir = choice.attributes
        # remove candidates that are worse in every attribute
        copy = []
        for can in self.candidates:
            if np.all(np.array(list(can.get_attr())) <
                      np.array(list(self._nadir.values()))):
                copy.append(can)
        for c in copy:
            self.candidates.remove(c)
        # calculate new ideal point
        for att in self.attribs:
            min = None
            max = None
            for candidate in self.candidates:
                temp = candidate.attributes[att]
                if min is None or temp < min:
                    min = temp
                if max is None or temp > max:
                    max = temp
            self._ideal[att] = min
            self._nadir[att] = max
        self._update()

    def virtualCandidateGen(self):
        '''Generate virtual candidates by selecting points between
        the nadir point and the the kmeans center'''
        X = []
        for can in self.candidates:
            X.append(np.array(list(can.get_attr())))
        if self._ns > len(self.candidates):
            self._ns = len(self.candidates)
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=self._ns).fit(np.array(X))
        centers = kmeans.cluster_centers_
        # project to the line between pareto front and nadir point
        if self._h == 1:
            numerator = 1
        else:
            numerator = self._h - 1
        centers = centers+(np.array(list(self._nadir.values()))-centers) *\
            (numerator/self._h)
        res = []
        for index, system in enumerate(centers):
            res.append(Candidate(index,
                                 dict(zip(self.attribs, system))))
        return res

    def _update(self):
        '''Update new query and the number of questions remained'''
        if (self._h > 0) and (len(self.candidates) != 1):
            self._query = self.virtualCandidateGen()
            self._h = self._h - 1
        else:
            self._query = None

    @staticmethod
    def description():
        return "E-NAUTILUS eliciter"


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
        data = np.array(data)

        # metrics = scenario['metrics']
        # already pre-applied, we can assume lower is always better
        self.active = self._active_alg(
            data,
            yield_indices=True,
            **self._active_kw
        )
        self._update()

    def input(self, choice):
        if choice == self._query[0].name:
            val = 1
        else:
            val = -1
        self.active.put_response(val)
        self._update()

    def _update(self):
        if self.active.next_round():
            a, b = self.active.get_query()
            self._query = (self.candidates[a], self.candidates[b])
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

    @staticmethod
    def description():
        return "ActiveRanking description"


class ActiveMax(ActiveRanking):

    _active_alg = halfspace.HalfspaceMax
    _active_kw = {'query_order': halfspace.max_compar_rand}

    @staticmethod
    def description():
        return "ActiveMax description"


class ActiveMaxSmooth(ActiveRanking):

    _active_alg = halfspace.HalfspaceMax
    _active_kw = {'query_order': halfspace.max_compar_smooth}

    @staticmethod
    def description():
        return "ActiveMaxSmooth description"


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

    @staticmethod
    def description():
        return "ActiveMaxPrimary description"


# export a list of eliciters
algorithms = {
    "Toy": Toy,
    "ActiveRanking": ActiveRanking,
    "ActiveMax": ActiveMax,
    "ActiveMaxSmooth": ActiveMaxSmooth,
    "ActiveMaxPrimary": ActiveMaxPrimary,
    "VotingEliciter": VotingEliciter,
    "Enautilus": Enautilus
}
