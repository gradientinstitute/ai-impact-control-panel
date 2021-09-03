'''Halfspace active ranking.

This implements the algorithm described in:

Jamieson, K.G., Nowak, R., 2011. Active Ranking using Pairwise Comparisons.
Advances in Neural Information Processing Systems (NeurIPS) 24, 9.
'''
import numpy as np
from functools import cmp_to_key
from scipy.optimize import linprog


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
    h: Hyperplane(plane, coef)
        A (named) tuple defining a hyperplane that is equidistant from points
        `a` and `b`. The tuple is of the form (plane, coef) where plane is a
        vector of shape (d,) defining the plane, and coef is a scalar defining
        the halfspaces. I.e. the equation of the plane is;

            plane_1 . x_1 + ... + plane_d . x_d >= coef
    '''
    # compute the midpoint
    mp = (a + b) / 2

    # compute the vector joining a and b
    ab = b - a

    # compute the separating hyperplane as normal to ab and passing through mp
    h = np.append(ab, mp @ ab)
    return h


def rank_ef_ex(X, oracle_fn):
    '''Rank objects using the exhaustive error free oracle algorithm.'''
    n, d = X.shape
    nC2 = (n * (n - 1)) // 2
    Y = np.zeros(nC2)
    H = np.zeros((nC2, d+1))
    Q = np.zeros((n, n), dtype=int)

    c = 0
    for j in range(1, n):
        for i in range(j):
            H[c, :] = hyperplane(X[j], X[i])
            impute_label(H[:c+1], Y[:c+1])
            if Y[c] == 0:
                Y[c] = oracle_fn(X[j], X[i])
            Q[j, i] = Y[c]
            Q[i, j] = - Y[c]
            c += 1

    # rank = binary sort positions in X using the comparisons in query_map
    key = cmp_to_key(lambda a, b: - Q[a, b])
    rank = sorted(range(n), key=key)
    return rank


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
    '''Attempt to impute a label of a query, the last object in H.'''
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
