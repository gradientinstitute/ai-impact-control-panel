'''Halfspace active ranking.

This implements the algorithm described in:

Jamieson, K.G., Nowak, R., 2011. Active Ranking using Pairwise Comparisons.
Advances in Neural Information Processing Systems (NeurIPS) 24, 9.
'''
import numpy as np
from functools import cmp_to_key
from scipy.optimize import linprog


#
#  Helper classes
#

class ShuffleUnshuffle():
    '''Helper class for shuffling then un-shuffling objects.

    Parameters
    ----------
    random_state: int, RandomState
        The random seed or RandomState object to be used for randomly shuffling
        the data.
    '''

    def __init__(self, random_state=None):
        '''Initialise a ShuffleUnshuffle object.'''
        if isinstance(random_state, np.random.RandomState):
            self.random = random_state
        else:
            self.random = np.random.RandomState(random_state)

    def shuffle(self, X):
        '''Shuffle an array of object by their first axis.

        Parameters
        ----------
        X: ndarray
            The array of object to shuffle.

        Returns
        -------
        X_shuffled: ndarray
            A copy of the array, but shuffled.
        '''
        self.n = len(X)
        self.pind = self.random.permutation(self.n)  # permutation
        self.ipind = np.empty(self.n, dtype=int)
        self.ipind[self.pind] = np.arange(self.n)  # inverse permutation
        X_shuffled = np.copy(X[self.pind])
        return X_shuffled

    def unshuffle(self, X_shuffled):
        '''Un-shuffle an array of object by their first axis.

        Parameters
        ----------
        X_shuffled: ndarray
            The array of object to un-shuffle.

        Returns
        -------
        X: ndarray
            A copy of the array, but unshuffled.
        '''
        if not hasattr(self, 'pind'):
            raise RuntimeError('No call to shuffle() has yet been made.')
        if len(X_shuffled) != self.n:
            raise RuntimeWarning('The length of the object to unshuffle is '
                                 'different from the original.')
        X = np.copy(X_shuffled[self.ipind])
        return X


#
# Ranking utilities
#

def hyperplane(a, b):
    '''Compute the plane equidistant from points a and b.

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
    '''
    # compute the midpoint
    mp = (a + b) / 2

    # compute the vector joining a and b
    ab = b - a

    # compute the separating hyperplane as normal to ab and passing through mp
    h = np.append(ab, mp @ ab)
    return h


def shatter_test(X, Y, return_hp=False):
    '''Test to see if the points in (X, Y) can be shattered by a hyperplane.

    This runs a linear program to see if the points in X labelled by Y can be
    shattered by a homogeneous linear separator (hyperplane containing the
    origin). Specifically, the following linear program is used,

        min_{w, s} s
        s.t.    Y * X @ w + s >= 1
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
    '''
    n, d = X.shape
    c = np.array([0.] * d + [1.])  # encodes min_{w, s} s
    A_ub = - np.vstack((Y * X.T, np.ones(n))).T  # Y * X @ w + s
    b_ub = np.full(n, -1.)
    bounds = [(None, None)] * d + [(0., None)]  # s >= 0
    res = linprog(c, A_ub, b_ub, bounds=bounds, method='highs')
    shattered = res.x[-1] < 1e-10
    if return_hp:
        return shattered, res.x[:-1]
    return shattered


def impute_label(H, Y):
    '''Attempt to impute a label of a query, which is the last object in H.

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
    '''
    assert len(H) == len(Y)

    if len(Y) < 2:
        return 0

    # Test if the query could be positive
    Y[-1] = 1
    positive = shatter_test(H, Y)

    # Test if the query could be negative
    Y[-1] = -1
    negative = shatter_test(H, Y)

    # If positive and negative, then the query is ambiguous
    if positive and negative:
        Y[-1] = 0
    elif positive and not negative:
        Y[-1] = 1
    elif negative and not positive:
        Y[-1] = -1
    else:
        raise RuntimeError('Ranking has become inconsistent!')


def robust_impute_label(H, Y):
    '''Attempt to impute a label of a query, which is the last object in H.

    This uses a strategy that is robust to noisy oracle inputs.
    '''
    raise NotImplementedError


#
#  Ranking algorithms
#

class _HalfspaceBase():

    def __init__(self, X, yield_indices=False):
        self.indices = yield_indices
        self.result = None
        self.response = None
        self.query_gen = self._algorithm(X)
        self.query = next(self.query_gen)
        self.__first_round = True

    def next_round(self):
        '''Initiate the next round of query-response from the algorithm.

        Returns
        -------
        bool:
            `True` if there is a new query ready, `False` if the algorithm is
            finished and the result is ready.
        '''
        if self.__first_round:
            self.__first_round = False
        else:
            try:
                self.query = self.query_gen.send(self.response)
            except StopIteration:
                return False
        return True

    def get_query(self):
        '''Get a query.

        Returns
        -------
        tuple:
            two objects (x_1, x_2) to compare, in particular x_1 < x_2 ?
        '''
        return self.query

    def put_response(self, response):
        '''Give a response to the query.

        Parameters
        ----------
        response: int
            response to the query, x_1 < x_2? -1 if true, else 1.
        '''
        self.response = response

    def get_result(self):
        '''Get the final result from the algorithm.

        Returns
        -------
        result: None or Any
            Returns None if there is no result ready, or the result, the type
            of which depends on the algorithm.
        '''
        return self.result

    def _algorithm(self, X):
        raise NotImplementedError('HalfspaceBase is a base class only.')


class HalfspaceRanking(_HalfspaceBase):
    '''Rank objects using the exhaustive active ranking algorithm.

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

    TODO
    ----
    Implement and hook up the robust label imputation algorithm.
    '''

    def _algorithm(self, X):
        n, d = X.shape
        nC2 = (n * (n - 1)) // 2  # number of unique pairwise comparisons
        Y = np.zeros(nC2)  # query labels
        H = np.zeros((nC2, d+1))  # query hyperplanes
        Q = np.zeros((n, n), dtype=int)  # All query labels, including reverse

        # Note we have not randomly shuffled X.
        c = 0
        for j in range(1, n):
            for i in range(j):
                H[c, :] = hyperplane(X[j], X[i])  # equidistant hyperplane
                impute_label(H[:c+1], Y[:c+1])  # impute hyperplane/query label
                if Y[c] == 0:  # cannot impute label
                    y = (yield j, i) if self.indices else (yield X[j], X[i])
                    if y is None:
                        raise RuntimeError('Expecting a query response.')
                    Y[c] = y
                Q[j, i], Q[i, j] = Y[c], - Y[c]  # query label, reverse query
                c += 1

        # binary sort positions in X using the comparisons in query_map
        key = cmp_to_key(lambda a, b: Q[a, b])
        self.result = np.array(sorted(range(n), key=key))


class HalfspaceMax(_HalfspaceBase):
    '''Find the max object using the halfspace comparison algorithm.

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

    TODO
    ----
    Implement and hook up the robust label imputation algorithm.
    '''

    def _algorithm(self, X):
        n, d = X.shape
        Y = np.zeros(n-1)  # query labels
        H = np.zeros((n-1, d+1))  # query hyperplanes
        mi = 0

        for q, i in zip(range(0, n-1), range(1, n)):
            H[q, :] = hyperplane(X[mi], X[i])
            impute_label(H[:i], Y[:i])
            if Y[q] == 0:  # cannot impute label
                y = (yield mi, i) if self.indices else (yield X[mi], X[i])
                if y is None:
                    raise RuntimeError('Expecting a query response.')
                Y[q] = y
            if Y[q] == -1:
                mi = i
        self.result = mi
