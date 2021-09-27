'''Test the model scoring functions.'''
import numpy as np
import pytest

from deva.score import eo_adv, eo_adv_rate, eo_disadv, eo_disadv_rate

N = 100000
N_A = 100000
PY = 0.8


def gen_eo_labels(tpr, tpr_a, random):
    '''generate eo fairness data.'''
    a = np.concatenate((np.zeros(N), np.ones(N_A)))
    y = random.binomial(n=1, p=PY, size=N + N_A)
    y_hat = y.copy()
    y_hat[:N] *= random.binomial(n=1, p=tpr, size=N)
    y_hat[N:] *= random.binomial(n=1, p=tpr_a, size=N_A)
    return y, y_hat, a


@pytest.mark.parametrize('tpr_a', [0.7, 0.8, 0.9])
def test_eo_disadv_rate(random, tpr_a):
    '''Test equality of opportunity rate for the disadvantaged class.'''
    tpr = 0.8
    y, y_hat, a = gen_eo_labels(tpr, tpr_a, random)

    eo = max(0, tpr - tpr_a)
    eo_hat = eo_disadv_rate(y, y_hat, None, a)

    assert np.allclose(eo_hat, eo, atol=1e-2)


@pytest.mark.parametrize('tpr_a', [0.7, 0.8, 0.9])
def test_eo_adv_rate(random, tpr_a):
    '''Test equality of opportunity rate for the advantaged class.'''
    tpr = 0.8
    y, y_hat, a = gen_eo_labels(tpr, tpr_a, random)

    eo = max(0, tpr_a - tpr)
    eo_hat = eo_adv_rate(y, y_hat, None, a)

    assert np.allclose(eo_hat, eo, atol=1e-2)


@pytest.mark.parametrize('tpr_a', [0.7, 0.8, 0.9])
def test_eo_disadv(random, tpr_a):
    '''Test equality of opportunity for the disadvantaged class.'''
    tpr = 0.8
    y, y_hat, a = gen_eo_labels(tpr, tpr_a, random)

    eo = max(0, tpr * N - tpr_a * N_A) * PY
    eo_hat = eo_disadv(y, y_hat, None, a)

    assert np.allclose(eo_hat, eo, rtol=5e-2, atol=500)


@pytest.mark.parametrize('tpr_a', [0.7, 0.8, 0.9])
def test_eo_adv(random, tpr_a):
    '''Test equality of opportunity for the advantaged class.'''
    tpr = 0.8
    y, y_hat, a = gen_eo_labels(tpr, tpr_a, random)

    eo = max(0, tpr_a * N - tpr * N_A) * PY
    eo_hat = eo_adv(y, y_hat, None, a)

    assert np.allclose(eo_hat, eo, rtol=5e-2, atol=500)
