'''Test the halfspace ranking algorithm.'''
import pytest
import numpy as np
from functools import partial
from deva import halfspace


def test_hyperplane(random):
    '''Test hyperplane returns expected objects.'''
    a = random.randn(10)
    b = random.randn(10)

    h = halfspace.hyperplane(a, b)

    assert len(h) == (len(a) + 1)
    a_hs = h[:-1] @ a - h[-1]
    assert a_hs < 0
    b_hs = h[:-1] @ b - h[-1]
    assert b_hs > 0


def test_shatter(shatterable_data):
    '''Test the shatter test can actually shatter points.'''
    # This can be shattered
    X, Y = shatterable_data
    assert halfspace.shatter_test(X, Y)

    # This cannot be shattered
    Y[0] = -1.
    assert not halfspace.shatter_test(X, Y)


def test_impute_label(shatterable_data):
    '''Test that label imputation works correctly.'''
    X, Y = shatterable_data

    # This should be a positive label
    X = np.vstack((X, [2, 2]))
    Y = np.append(Y, 0)
    halfspace.impute_label(X, Y)
    assert Y[-1] > 0

    # This should be a negative label
    X[-1, :] = np.array([-2, -2])
    halfspace.impute_label(X, Y)
    assert Y[-1] < 0

    # This label should be ambiguous
    X[-1, :] = np.array([0, -2])
    halfspace.impute_label(X, Y)
    assert Y[-1] == 0


def test_impute_label_random_order(random, shatterable_data):
    '''Test that label imputation correctly with out of order queries.'''
    X, Y = shatterable_data
    n = len(Y)
    perm = random.permutation(n)
    X = X[perm, :]
    Y = Y[perm]

    Y_hat = np.zeros_like(Y)
    Y_hat[0] = Y[0]

    for i in range(2, n+1):
        halfspace.impute_label(X[:i], Y_hat[:i])
        if Y_hat[i-1] == 0:
            Y_hat[i-1] = Y[i-1]

    assert np.all(Y == Y_hat)


def test_arank(random):
    '''Test the ranking algorithm'''
    n = 30
    X = random.multivariate_normal(
        mean=[0, 0],
        cov=[[3., 1.], [1., 1.5]],
        size=n
    )
    r = np.array([-1, 1])  # reference point for defining the ranking origin
    cnt = 0

    def oracle_fn(a, b):
        nonlocal r, cnt
        cnt += 1
        ar = ((a - r)**2).sum()
        br = ((b - r)**2).sum()
        return -1 if ar < br else 1

    ranker = halfspace.HalfspaceRanking(
        X,
        query_order=halfspace.rank_compar_ord
    )
    while ranker.next_round():
        a, b = ranker.get_query()
        ranker.put_response(oracle_fn(a, b))

    dist = ((X - r)**2).sum(axis=1)
    true_ranks = np.argsort(dist)
    assert np.all(true_ranks == ranker.get_result())
    assert cnt < n * (n - 1) // 2


@pytest.mark.parametrize('query_order', [
    halfspace.max_compar_smooth,
    halfspace.max_compar_rand,
    partial(halfspace.max_compar_primary, primary_index=0)
])
def test_amax(random, query_order):
    '''Test the active max algorithm'''
    n = 30
    X = random.multivariate_normal(
        mean=[0, 0],
        cov=[[3., 1.], [1., 1.5]],
        size=n
    )
    r = np.array([-1, 1])  # reference point for defining the ranking origin
    cnt = 0

    def oracle_fn(a, b):
        nonlocal r, cnt
        cnt += 1
        ar = ((a - r)**2).sum()
        br = ((b - r)**2).sum()
        return -1 if ar < br else 1

    maxer = halfspace.HalfspaceMax(X, query_order=query_order)
    while maxer.next_round():
        a, b = maxer.get_query()
        maxer.put_response(oracle_fn(a, b))

    dist = ((X - r)**2).sum(axis=1)
    true_max = np.argmax(dist)
    assert np.all(true_max == maxer.get_result())
    assert cnt < n
