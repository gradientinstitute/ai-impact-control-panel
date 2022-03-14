"""Preferene eliciter module."""
import numpy as np
from deva import halfspace
from sklearn.cluster import KMeans


class Candidate:
    """Represent a candidate model's name and attributes."""

    def __init__(self, name, attributes, spec_name=None):
        self.name = name
        self.attr_keys = sorted(attributes.keys())
        self.attr_values = [attributes[a] for a in self.attr_keys]
        self.attributes = dict(zip(self.attr_keys, self.attr_values))
        self.spec_name = spec_name or name

    def __getitem__(self, key):
        """Access attributes directly."""
        return self.attributes[key]

    def __repr__(self):
        """Display candidate by name."""
        return f"Candidate({self.name})"

    def get_attr_values(self):
        """Return sorted attribute values."""
        return self.attr_values

    def get_attr_keys(self):
        """Return sorted attribute keys."""
        return self.attr_keys


class Eliciter:
    """Base class for elicitation algorithms."""

    # Just a promise that inheriting classes will have these members
    def terminated(self):
        """Check whether the eliciter is finished."""
        raise NotImplementedError

    def query(self):
        """Collect the options the algorithm is presenting to the user."""
        raise NotImplementedError

    def result(self):
        """Return the preferred candidate."""
        raise NotImplementedError

    def put(self, choice):
        """Input a user preference."""
        raise NotImplementedError

    @classmethod
    def description(cls):
        """Return the first line of the docstring (by default)."""
        lines = cls.__doc__.split("\n")
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if len(line)]
        return lines[0] if lines else "An elicitation algorithm."


class LadderEliciter(Eliciter):
    """Pass over the candidates, comparing each to the current preference."""

    def __init__(self, candidates, scenario):
        assert candidates, "No candidate models"
        Eliciter.__init__(self)
        self.candidates = list(candidates)  # copy references
        self._update()

    def put(self, choice):
        """Input user decision into the eliciter."""
        if choice == self._query[1].name:
            self.candidates.remove(self._query[0])
        else:
            self.candidates.remove(self._query[1])
        self._update()

    def terminated(self):
        """Check if eliciter is terminated."""
        return len(self.candidates) == 1

    def result(self):
        """Obtain eliciter final result."""
        assert len(self.candidates) == 1, "Not terminated."
        return self.candidates[0]

    def query(self):
        """Obtain eliciter current query."""
        return self._query

    def _update(self):
        if len(self.candidates) > 1:
            self._query = (self.candidates[0], self.candidates[1])
        else:
            self._query = None


class EnautilusEliciter(Eliciter):
    """
    Use E-NAUTILUS to incrementally step from nadir to an efficient candidate.

    See: 'E-NAUTILUS: A decision support system for complex multiobjective
    optimization problems based on the NAUTILUS method.', Ruiz et al. 2015
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
        self._h = 8  # number of questions
        self._ns = 2  # number of options
        self.iter_count = 0
        self.candidates = list(candidates)
        self.attribs = candidates[0].get_attr_keys()
        self.current_centers = []
        self.kmeans_centers = []
        self._update_zpoints()
        self._update()

    def _set_config(self, n1, ns):
        """Update the number of questions the algorithm will use."""
        self._h = n1 + 1
        self._ns = ns
        self._update()

    def query(self):
        """Return the current query."""
        return self._query

    def terminated(self):
        """Check if the termination condition is met."""
        return (self._h <= 0) or (len(self.candidates) == 1)

    def result(self):
        """Return result of the eliciter if terminated."""
        assert (self._h <= 0) or (len(self.candidates) == 1), "Not terminated."
        X = []
        for can in self.candidates:
            X.append(np.array(can.get_attr_values()))
        sub = np.array(X) - np.array(list(self._nadir.values()))
        norm1 = np.linalg.norm(sub, axis=1)
        return self.candidates[norm1.argmin()]

    def _update_zpoints(self):
        """Calculate new ideal and nadirpoint."""
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
        self._nadir = choice.attributes
        # remove candidates that are worse in every attribute
        copy = []
        for can in self.candidates:
            if np.any(np.array(can.get_attr_values())
                      > np.array(list(self._nadir.values()))):
                copy.append(can)
        for c in copy:
            self.candidates.remove(c)
        self._update_zpoints()
        self._nadir = choice.attributes
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
        kmeans = KMeans(n_clusters=self._ns).fit(np.array(X))
        centers = kmeans.cluster_centers_
        kc = []
        for c in centers:
            sub = np.array(X) - np.array(c)
            norm1 = np.linalg.norm(sub, axis=1)
            kc.append(X[norm1.argmin()])
        kc = np.array(kc)
        self.kmeans_centers = kc
        # project to the line between pareto front and nadir point
        if self._h == 1:
            numerator = 1
        else:
            numerator = self._h - 1
        kc = kc + (
            (np.array(list(self._nadir.values())) - kc)
            * numerator / self._h
        )
        self.current_centers = kc
        res = []
        step = ""  # TODO: make a different letter for each step
        for index, system in enumerate(kc):
            cname = f"{step}{index}"
            res.append(Candidate(cname,
                                 dict(zip(self.attribs, system))))
        return res

    def _update(self):
        """Update new query and the number of questions remaining."""
        if (self._h > 0) and (len(self.candidates) != 1):
            self._query = self.virtualCandidateGen()
            self._h = self._h - 1
        else:
            self._query = None


class ActiveMaxEliciter(Eliciter):
    """Use pairwise linear separation to estimate the preferred candidate."""

    _active_alg = halfspace.HalfspaceMax
    _active_kw = {"query_order": halfspace.max_compar_rand}
    # Orders: max_compar_smooth, max_compar_rand,
    #         partial(max_compar_primary, primary_index=...)

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
        """Input user decision into the eliciter."""
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

    def result(self):
        """Return eliciter result."""
        return self._result

    def query(self):
        """Get current eliciter query."""
        return self._query

    def terminated(self):
        """Check if current model is terminated."""
        return self._result is not None


# Export all the Eliciter classes
algorithms = {
    "Ladder": LadderEliciter,
    "ActiveMax": ActiveMaxEliciter,
    "E-NAUTILUS": EnautilusEliciter,
}
