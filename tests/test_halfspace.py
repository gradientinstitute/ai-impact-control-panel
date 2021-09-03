'''Test the halfspace ranking algorithm.'''
import numpy as np
from deva.halfspace import hyperplane, shatter_test, impute_label, rank_ef_ex


def test_hyperplane(random):
    '''Test hyperplane returns expected objects.'''
    a = random.randn(10)
    b = random.randn(10)

    h = hyperplane(a, b)

    assert len(h) == (len(a) + 1)
    a_hs = h[:-1] @ a - h[-1]
    assert a_hs < 0
    b_hs = h[:-1] @ b - h[-1]
    assert b_hs > 0


def test_shatter(shatterable_data):
    '''Test the shatter test can actually shatter points.'''
    # This can be shattered
    X, Y = shatterable_data
    assert shatter_test(X, Y)

    # This cannot be shattered
    Y[0] = -1.
    assert not shatter_test(X, Y)


def test_impute_label(shatterable_data):
    '''Test that label imputation works correctly.'''
    X, Y = shatterable_data

    # This should be a positive label
    X = np.vstack((X, [2, 2]))
    Y = np.append(Y, 0)
    impute_label(X, Y)
    assert Y[-1] > 0

    # This should be a negative label
    X[-1, :] = np.array([-2, -2])
    impute_label(X, Y)
    assert Y[-1] < 0

    # This label should be ambiguous
    X[-1, :] = np.array([0, -2])
    impute_label(X, Y)
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
        impute_label(X[:i], Y_hat[:i])
        if Y_hat[i-1] == 0:
            Y_hat[i-1] = Y[i-1]

    assert np.all(Y == Y_hat)


def test_ranking(random):
    '''Test the ranking algorithm'''
    n = 30
    X = random.randn(n, 2) * 2
    r = np.array([-1, 1])
    cnt = 0

    def oracle_fn(a, b):
        nonlocal r, cnt
        cnt += 1
        ar = ((a - r)**2).sum()
        br = ((b - r)**2).sum()
        return 1 if ar <= br else -1

    dist = ((X - r)**2).sum(axis=1)
    true_ranks = np.argsort(dist)
    ranks = rank_ef_ex(X, oracle_fn)
    assert np.all(true_ranks == ranks)
    assert cnt < n * (n - 1) // 2
