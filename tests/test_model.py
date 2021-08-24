"""Tests for the model module."""

import numpy as np

from deva.model import apply_threshold


def test_apply_threshold():
    '''Test thresholds for protected attributes are being applied properly.'''
    y_scores = np.concatenate(([0.3] * 20, [0.7] * 20))
    n = len(y_scores)
    sensitive = np.random.binomial(n=1, p=0.5, size=n).astype(int)

    # Single threshold
    threshold = 0.6
    y_pred_true = y_scores > threshold
    y_pred = apply_threshold(threshold, None, y_scores, None)
    assert all(y_pred == y_pred_true.astype(int))

    # Threshold per sensitive class
    threshold_protected = 0.2
    y_pred_true = np.logical_or(y_scores > 0.5, sensitive.astype(bool))
    y_pred = apply_threshold(threshold, threshold_protected, y_scores,
                             sensitive)
    assert all(y_pred == y_pred_true.astype(int))
