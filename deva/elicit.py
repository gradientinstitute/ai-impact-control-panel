"""Preference eliciter module."""
from itertools import combinations
from functools import partial
import numpy as np
from deva import halfspace
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from collections import OrderedDict


class Candidate:
    """Represent a candidate model's name and attributes."""

    def __init__(self, name, attributes, spec_name=None):
        self.name = name
        self.attr_keys = sorted(list(attributes.keys()))
        self.attr_values = [attributes[a] for a in self.attr_keys]
        self.attributes = dict(zip(self.attr_keys, self.attr_values))
        self.spec_name = spec_name or name

    def __getitem__(self, key):
        """Access attributes directly."""
        return self.attributes[key]

    def __repr__(self):
        """Human readable display of candidate."""
        return f"Candidate({self.name})"

    def get_attr_values(self):
        return self.attr_values

    def get_attr_keys(self):
        return self.attr_keys


class Eliciter:
    """Base class for elicitation algorithms."""

    # Just a promise that inheriting classes will have these members
    def terminated(self, choice):
        """Check whether the eliciter is finished."""
        raise NotImplementedError

    @property
    def query(self, choice):
        """Collect the options the algorithm is presenting to the user."""
        raise NotImplementedError

    @property
    def result(self, choice):
        """Return the preferred candidate."""
        raise NotImplementedError

    def put(self, choice):
        """Input a user preference."""
        raise NotImplementedError

    @staticmethod
    def description():
        # placeholder for the description of eliciter
        raise NotImplementedError


class VotingEliciter(Eliciter):
    """Simple eliciter that chooses the most selected candidate."""

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

    def put(self, choice):
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
    """Simple eliciter with sequential elimination."""

    def __init__(self, candidates, scenario):
        assert candidates, "No candidate models"
        Eliciter.__init__(self)
        self.candidates = list(candidates)  # copy references
        self._update()

    def put(self, choice):
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
    """
    Enautilus eliciter.

    See: E-NAUTILUS: A decision support system for complex multiobjective
    optimization problems based on the NAUTILUS method.
    """
    def __init__(self, candidates, scenario):
        """
        Initialise Enautilus.

        Generate initial ideal point and ndair point from the given candidates,
        and extract attributes of the candidates.
        """
        if len(candidates) < 2:
            raise RuntimeError("Two or more candidates required.")
        Eliciter.__init__(self)
        self._nadir = {}
        self._ideal = {}
        self._h = 5  # number of questions
        self._ns = 2  # number of options
        self.candidates = list(candidates)
        self.attribs = candidates[0].get_attr_keys()
        self.current_centers = []
        self._update_zpoints()
        self._update()

    def get_z_points(self):
        """Return ideal point and nadir point in a list."""
        return [self._ideal, self._nadir]

    def updateForN(self, n1, ns):
        """Update the number of questions the algorithm will use."""
        self._h = n1 + 1
        self._ns = ns
        self._update()

    @property
    def query(self):
        """Return the current query."""
        return self._query

    @property
    def terminated(self):
        """Check if the termination condition is met."""
        return (self._h <= 0) or (len(self.candidates) == 1)

    @property
    def result(self):
        """Return result of the eliciter if terminated."""
        assert (self._h <= 0) or (len(self.candidates) == 1), "Not terminated."
        X = []
        for can in self.candidates:
            X.append(np.array(can.get_attr_values()))
        return self.candidates[
            np.linalg.norm(np.array(X)
                           - np.array(list(self._nadir.values()))).argmin()
        ]

    def _update_zpoints(self):
        """calculate new ideal and nadirpoint"""
        for att in self.attribs:
            minv = None
            maxv = None
            for candidate in self.candidates:
                temp = candidate.attributes[att]
                if minv is None or temp < minv:
                    minv = temp
                if maxv is None or temp > maxv:
                    maxv = temp
            self._ideal[att] = minv
            self._nadir[att] = maxv

    def put(self, choice):
        """Receive input from the user and update ideal point."""
        choice = self._query[int(choice)]
        # import IPython;IPython.embed()
        self._nadir = choice.attributes
        print(self._nadir)
        # import IPython;IPython.embed()
        # remove candidates that are worse in every attribute
        copy = []
        for can in self.candidates:
            if np.all(np.array(can.get_attr_values())
                      < np.array(list(self._nadir.values()))):
                copy.append(can)
        for c in copy:
            self.candidates.remove(c)
        self._update_zpoints()
        self._update()

    def virtualCandidateGen(self):
        """
        Generate virtual candidates.

        Selects points between the nadir point and the the kmeans centers.
        """
        X = []
        for can in self.candidates:
            X.append(np.array(can.get_attr_values()))
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
        centers = centers + (
            (np.array(list(self._nadir.values())) - centers)
            * numerator / self._h
        )
        self.current_centers = centers
        res = []
        step = ""  # TODO: make a different letter for each step
        for index, system in enumerate(centers):
            cname = f"{step}{index}"
            res.append(Candidate(cname,
                                 dict(zip(self.attribs, system))))
        return res

    def _update(self):
        """Update new query and the number of questions remaining."""
        if (self._h > 0) and (len(self.candidates) != 1):
            self._query = self.virtualCandidateGen()
            self._h = self._h - 1
            self.plot_2d()
        else:
            self._query = None

    @staticmethod
    def description():
        return "E-NAUTILUS eliciter"

    def plot_2d(self):
        """plot 2d scenarios according to the paper"""
        plt.figure()
        width = self._nadir[self.attribs[0]] - self._ideal[self.attribs[0]]
        height = self._nadir[self.attribs[1]] - self._ideal[self.attribs[1]]
        currentAxis = plt.gca()
        currentAxis.add_patch(Rectangle((self._ideal[self.attribs[0]],
                              self._ideal[self.attribs[1]]),
                              width, height, fill=None, alpha=0.1))
        plt.scatter(self._ideal[self.attribs[0]], self._ideal[self.attribs[1]],
                    s=80, marker=(5, 1), label='ideal point')
        plt.scatter(self._nadir[self.attribs[0]], self._nadir[self.attribs[1]],
                    s=80, marker=(3, 1), label='nadir point')
        for point in self.current_centers:
            plt.scatter(point[0], point[1], c='black', label='centers')
        for can in self.candidates:
            point1 = np.array(can.get_attr_values())
            plt.scatter(point1[0], point1[1], c='red', alpha=0.3,
                        label='candidates')
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys())
        plt.savefig(f"last {self._h} plot.jpg")


# Eliciter implementations
class ActiveRanking(Eliciter):
    """Implements an eliciter based on linear plane queries."""

    _active_alg = halfspace.HalfspaceRanking
    _active_kw = {"query_order": halfspace.rank_compar_ord}

    def __init__(self, candidates, scenario):
        if len(candidates) < 2:
            raise RuntimeError("Two or more candidates required.")
        Eliciter.__init__(self)
        self.candidates = list(candidates)
        attribs = list(candidates[0].attributes.keys())
        self._result = None

        # convert data structures to a numpy array
        data = []
        for c in candidates:
            data.append([c[a] for a in attribs])
        data = np.array(data)

        # metrics = scenario["metrics"]
        # already pre-applied, we can assume lower is always better
        self.active = self._active_alg(
            data,
            yield_indices=True,
            **self._active_kw
        )
        self._update()

    def put(self, choice):
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
    """Elicit the preferred candidate using pairwise linear separation."""

    _active_alg = halfspace.HalfspaceMax
    _active_kw = {"query_order": halfspace.max_compar_rand}

    @staticmethod
    def description():
        return "ActiveMax description"


class ActiveMaxSmooth(ActiveRanking):
    """
    Elicit the preferred candidate using pairwise linear separation.

    Distinct from ActiveMax by using a query order heuristic.
    """

    _active_alg = halfspace.HalfspaceMax
    _active_kw = {"query_order": halfspace.max_compar_smooth}

    @staticmethod
    def description():
        return "ActiveMaxSmooth description"


class ActiveMaxPrimary(ActiveRanking):
    """
    Elicit the preferred candidate using pairwise linear separation.

    Distinct from ActiveMax by using a query order based on a primary metric.
    """

    _active_alg = halfspace.HalfspaceMax

    def __init__(self, candidates, scenario):
        if "primary_metric" not in scenario:
            raise RuntimeError("Expecting a primary_metric to be specified in"
                               " the metadata.")
        pmetric = scenario["primary_metric"]
        attribs = list(candidates[0].attributes.keys())
        pri_ind = attribs.index(pmetric)
        qorder = partial(halfspace.max_compar_primary, primary_index=pri_ind)
        self._active_kw = {"query_order": qorder}
        super().__init__(candidates, scenario)

    @staticmethod
    def description():
        return "ActiveMaxPrimary description"


# Export all the Eliciter classes
algorithms = {
    "Toy": Toy,
    "ActiveRanking": ActiveRanking,
    "ActiveMax": ActiveMax,
    "ActiveMaxSmooth": ActiveMaxSmooth,
    "ActiveMaxPrimary": ActiveMaxPrimary,
    "VotingEliciter": VotingEliciter,
    "Enautilus": Enautilus
}
