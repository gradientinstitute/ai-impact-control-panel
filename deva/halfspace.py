"""Halfspace active ranking.

This implements the algorithm described in:

Jamieson, K.G., Nowak, R., 2011. Active Ranking using Pairwise Comparisons.
Advances in Neural Information Processing Systems (NeurIPS) 24, 9.

Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
"""

import numpy as np
from functools import cmp_to_key
from scipy.optimize import linprog
from sklearn.utils import check_random_state
from sklearn.decomposition import PCA


SHATTER_THRESH = 1e-10
EPS = 1e-5   # hack for constant column std


# Ranking algorithms


class _HalfspaceBase:

    def __init__(self):
        self.query = None
        self.response = None
        self.result = None
        # Don't allow instances of this base class
        raise NotImplementedError

    def next_round(self):
        """Initiate the next round of query-response from the algorithm.

        Returns
        -------
        bool:
            `True` if there is a new query ready
        """
        raise NotImplementedError

    def put_response(self, response):
        """Submit a response to the query.

        Parameters
        ----------
        response: int
            response to the query, x_1 < x_2? -1 if true, else 1.
        """
        raise NotImplementedError

    def get_result(self):
        """Get the final result from the algorithm."""
        return self.result

    def get_query(self):
        """Get a query.

        Returns
        -------
        tuple:
            two objects (x_1, x_2) to ask whether x_1 < x_2
        """
        return self.query


class HalfspaceRanking(_HalfspaceBase):
    """
    Rank objects using the exhaustive active ranking algorithm.

    This is the "exhaustive" algorithm because it computes ALL (n choose 2)
    pairwise ranking comparisons for n object. However, it expected that only d
    log n queries will be made to an oracle on average, where each object has d
    features. As the authors note (Jamieson and Nowak, 2011), the computational
    complexity of the algorithm can be reduced by integrating the query label
    inference into a binary sorting algorithm, rather than running the sort on
    the result of the (n choose 2) comparisons.

    Queries are of the form, x_1 < x_2. If this ordering is correct, the oracle
    should return -1, otherwise 1.

    This class should be used in a loop like follows,

    ```
    ranker = HalfspaceRanking(X)
    while ranker.next_round():
        a, b = ranker.get_query()
        preference = oracle_fn(a, b)  # preference should be {-1, 1}
        ranker.put_response(preference)

    ranks = ranker.get_result()
    ```

    Where `ranks` are integer indexes into the object array `X`.

    The primary assumption behind this algorithm is that rankings can be
    computed as:

        x_1 < x_2 <=> ||x_1 - r|| < ||x_2 - r||

    For some unique reference point, r, in R^d that defines the "origin" of the
    ranking.

    Parameters
    ----------
    X: ndarray
        The n-objects of shape (n, d) to be ranked.
    yield_indices: bool
        Yield indices into X (True) or the rows of X themselves (False) for the
        queries.
    """

    def __init__(self, X, query_order, yield_indices=False):

        self.yield_indices = yield_indices
        self.result = None
        self.query = None
        self.order = query_order(X)  # sequence of tuples
        self.X = X
        self.i = -1   # incremented before first use

        # Allocate storage buffers for imputation
        n, d = X.shape
        self.nc = (n * (n - 1)) // 2  # unique pairwise comparisons
        self.Y = np.zeros(self.nc)  # query labels
        self.H = np.zeros((self.nc, d + 1))  # query hyperplanes
        self.Q = np.zeros((n, n), dtype=int)  # All labels, including reversed

    def next_round(self):
        """Advance the eliciter to the next user-choice round."""
        assert not self.query

        for self.i in range(self.i + 1, self.nc):
            left, right = self.order[self.i]

            # construct hyperplane comparing left & right
            self.H[self.i, :] = hyperplane(self.X[left], self.X[right])

            # impute the label inplace to determine ambiguities
            if impute_label(self.H[:self.i + 1], self.Y[:self.i + 1]):
                self.put_response(self.Y[self.i])
            else:
                break
        else:
            # Comparisons exhausted - terminated
            # binary sort positions in X using the comparisons in query_map
            key = cmp_to_key(lambda a, b: self.Q[a, b])
            self.result = np.array(sorted(range(len(self.X)), key=key))
            return False  # no next round

        # Stopped at ambiguity
        self.query = (
            (left, right) if self.yield_indices
            else (self.X[left], self.X[right])
        )
        return True

    def put_response(self, y):
        """Inform the eliciter of the user's choice."""
        left, right = self.order[self.i]
        self.Y[self.i] = y
        self.Q[[left, right], [right, left]] = [y, -y]
        self.query = None  # unlock next_round


#
# Max algorithms
#

class HalfspaceMax(_HalfspaceBase):
    """Find the max object using the halfspace comparison algorithm.

    Queries are of the form, x_1 < x_2. If this ordering is correct, the oracle
    should return -1, otherwise 1.

    This class should be used in a loop like follows,

    ```
    maxer = HalfspaceRanking(X)
    while maxer.next_round():
        a, b = maxer.get_query()
        preference = oracle_fn(a, b)  # preference should be {-1, 1}
        maxer.put_response(preference)

    maximum = maxer.get_result()
    ```

    Where `maximum` is an integer index into the object array `X`.

    The primary assumption behind this algorithm is that rankings can be
    computed as:

        x_1 < x_2 <=> ||x_1 - r|| < ||x_2 - r||

    For some unique reference point, r, in R^d that defines the "origin" of the
    ranking.

    Parameters
    ----------
    X: ndarray
        The n-objects of shape (n, d) to be ranked.
    yield_indices: bool
        Yield indices into X (True) or the rows of X themselves (False) for the
        queries.
    query_order: callable
        A callable that returns the initial max object index guess and a
        sequence of indices for subsequent comparisons.
    """

    def __init__(self, X, query_order, yield_indices=False):

        self.yield_indices = yield_indices
        self.result = None
        self.query = None
        self.order = query_order(X)
        self.X = X[self.order]
        self.maxi = 0  # current preference
        self.i = 0    # incremented before use (starts from 1)

        # Allocate storage buffers for imputation
        self.n, d = X.shape
        self.Y = np.zeros(self.n - 1)  # comparison labels
        self.H = np.zeros((self.n - 1, d + 1))  # comparison hyperplanes

    def next_round(self):
        """Advance to the next round."""
        for self.i in range(self.i + 1, self.n):

            # construct hyperplane comparing candidate with best
            self.H[self.i - 1, :] = hyperplane(self.X[self.maxi],
                                               self.X[self.i])

            # impute label inplace to determine ambiguities
            if impute_label(self.H[:self.i], self.Y[:self.i]):
                self.put_response(self.Y[self.i - 1])
            else:
                break  # an ambiguity was found - let's ask the user
        else:
            # loop finished - terminate
            self.result = self.order[self.maxi]
            return False

        # We have two return behaviours depending on yield_indices
        ret = self.order if self.yield_indices else self.X
        self.query = (ret[self.maxi], ret[self.i])
        return True

    def put_response(self, y):
        """Inform the eliciter of the user's choice."""
        self.Y[self.i - 1] = y
        if y == -1:
            self.maxi = self.i
        self.query = None  # check next_round is only called after put_response


#
# Ranking utilities
#

def hyperplane(a, b):
    """Compute the plane equidistant from points a and b.

    Parameters
    ----------
    a: ndarray
        A point of shape (d,). This is the beginning point.
    b: ndarray
        A point of shape (d,). This is the ending point.

    Returns
    -------
    h: ndarray
        An array of coefficient defining a hyperplane that is equidistant from
        points `a` and `b`. The array is of the form [plane_1, ..., plane_d,
        coef] where plane is a vector of shape (d,) defining the plane, and
        coef is a scalar defining the halfspaces. I.e. the equation of the
        plane is;
            plane_1 . x_1 + ... + plane_d . x_d >= coef
    """
    # compute the midpoint
    mp = (a + b) / 2

    # compute the vector joining a and b
    ab = b - a

    # compute the separating hyperplane as normal to ab and passing through mp
    h = np.append(ab, mp @ ab)
    return h


def shatter_test(X, Y):
    r"""Test to see if the points in (X, Y) can be shattered by a hyperplane.

    This runs a linear program to see if the points in X labelled by Y can be
    shattered by a homogeneous linear separator (hyperplane containing the
    origin). Specifically, the following linear program is used,

    .. math::
        \min_{w, s} s
        \textrm{s.t.} Y * X @ w + s >= 1
                      s >= 0

    If s is zero, then the points can be separated by the hyperplane [w 0].
    Otherwise the solution to the plane separation problem, Y * X @ w >= 1 for
    any w is not feasible.

    This has been adapted from:
        https://stats.stackexchange.com/questions/182329/ \
            how-to-know-whether-the-data-is-linearly-separable

    Parameters
    ----------
    X: ndarray
        An array of N objects to shatter in (N, D).
    Y: ndarray
        An array of shape (N,) containing labels in {-1, 1}

    Returns
    -------
    bool:
        True the objects can be shattered by a homogeneous linear separator.
    """
    n, d = X.shape
    c = np.array([0.] * d + [1.])  # encodes min_{w, s} s
    A_ub = - np.vstack((Y * X.T, np.ones(n))).T  # Y * X @ w + s
    b_ub = np.full(n, -1.)
    bounds = [(None, None)] * d + [(0., None)]  # s >= 0
    res = linprog(c, A_ub, b_ub, bounds=bounds, method="highs")
    shattered = res.x[-1] < SHATTER_THRESH
    return shattered


def impute_label(H, Y):
    """Attempt to impute a label of a query, which is the last object in H.

    Parameters
    ----------
    H: ndarray
        An array of shape (n, d+1) hyperplanes containing (d+1,) dimensions
        hyperplanes. The query is the last point in this array.
    Y: ndarray
        An array of shape (n,) of hyperplane labels in {-1, 1}. The last
        element of this array will be we written into with the label of H[-1].
        A label of 0 means the label of the last point is ambiguous, and needs
        to be resolved by an oracle.

    Raises
    ------
    RuntimeError:
        If the hyperplanes can no longer be shattered by their labelling. This
        means inconsistent comparison labels have been given by the oracle.
        This function is not robust to a noisy oracle
    """
    assert len(H) == len(Y)

    if len(Y) < 2:
        return False

    # Test if the query could be positive
    Y[-1] = 1
    positive = shatter_test(H, Y)

    # Test if the query could be negative
    Y[-1] = -1
    negative = shatter_test(H, Y)

    # If positive and negative, then the query is ambiguous
    imputable = True
    if positive and negative:
        imputable = False
        Y[-1] = 0  # just in case
    elif positive and not negative:
        Y[-1] = 1
    elif negative and not positive:
        Y[-1] = -1
    else:
        raise RuntimeError("Ranking has become inconsistent!")
    return imputable


#
#  Query order generators
#

def max_compar_primary(X, primary_index):
    """Generate comparisons based on the order of the primary metric."""
    pmetric = X[:, primary_index]
    order = np.argsort(pmetric)[::-1]
    return order


def max_compar_smooth(X):
    """Generate "smoothly transitioning" pairwise comparisons."""
    Xstd = (X - X.mean(axis=0)) / X.std(axis=0)
    Xproj = np.squeeze(PCA(n_components=1).fit_transform(Xstd))
    order = np.argsort(Xproj)[::-1]  # largest first

    return order


def max_compar_rand(X, random_state=None):
    """Generate random comparisons, with the largest magnitude object first."""
    n = len(X)
    inds = list(range(n))

    # Standardise X
    Xstd = (X - X.mean(axis=0)) / (X.std(axis=0) + EPS)

    # Get the largest magnitude point for the first query
    norms = (Xstd**2).sum(axis=1)
    first = np.argmax(norms)

    # Find the most distant point for the second query
    second = np.argmax(((Xstd[first] - Xstd)**2).sum(axis=1))
    inds.remove(first)
    inds.remove(second)

    # All subsequent queries are random
    random = check_random_state(random_state)
    random_inds = random.permutation(inds)
    return np.concatenate(([first, second], random_inds))


def rank_compar_ord(X):
    """Generate all n choose 2 comparisons."""
    n = len(X)
    order = []
    for j in range(1, n):
        for i in range(j):
            order.append((j, i))

    return order
