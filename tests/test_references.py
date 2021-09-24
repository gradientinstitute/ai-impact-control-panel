'''Test the reference models.'''
import pytest
import numpy as np
import pandas as pd
# from sklearn.utils.estimator_checks import check_estimator

from deva.references import RandomClassifier


# Getting this working is more effort than it is worth.
# def test_estimator():
#     est = RandomClassifier()
#     check_estimator(est)


def test_no_sensitive(random):
    '''Test random predictor with no stratification.'''
    p_true = 0.2
    n = 500000
    X = random.randn(n, 2)  # This doesn't do anything
    y = random.binomial(n=1, p=p_true, size=n)

    clf = RandomClassifier(random_state=random)
    clf.fit(X, y)
    assert np.allclose(clf.py_, p_true, rtol=1e-2)
    assert np.allclose(clf.py_, clf.predict_proba(X)[:, 1])

    y_hat = clf.predict(X)
    p_hat = np.mean(y_hat)
    assert not np.allclose(y, y_hat)
    assert np.allclose(clf.py_, p_hat, rtol=1e-2)


@pytest.mark.parametrize('attr', ['protected', 1])
def test_stratification(random, attr):
    '''Test sensitive attribute stratification.'''
    n = 500000
    pa = 0.3
    py = 0.4
    pya = 0.6
    X = pd.DataFrame({
        'something random': random.randn(n),
        'protected': random.binomial(n=1, p=pa, size=n)
    })
    amask = X['protected'] == 1
    na = amask.sum()
    y = np.empty(n)
    y[amask] = random.binomial(n=1, p=pya, size=na)
    y[~amask] = random.binomial(n=1, p=py, size=n-na)

    clf = RandomClassifier(stratify_attribute=attr, random_state=random)
    clf.fit(X, y)
    assert isinstance(clf.py_, list)
    assert np.allclose(clf.py_[0], py, rtol=1e-2)
    assert np.allclose(clf.py_[1], pya, rtol=1e-2)

    p_pred = clf.predict_proba(X)[:, 1]
    assert np.allclose(clf.py_[0], p_pred[~amask])
    assert np.allclose(clf.py_[1], p_pred[amask])

    y_hat = clf.predict(X)
    pa_hat = np.mean(y_hat[amask])
    p_hat = np.mean(y_hat[~amask])
    assert np.allclose(clf.py_[0], p_hat, rtol=1e-2)
    assert np.allclose(clf.py_[1], pa_hat, rtol=1e-2)
