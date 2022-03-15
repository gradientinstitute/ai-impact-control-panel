"""
Pytest fixtures and utilities.

Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
"""

import numpy as np
import pytest


SEED = 666
RAND = np.random.RandomState(SEED)


@pytest.fixture
def random():
    """Get a random state."""
    return RAND


@pytest.fixture
def shatterable_data():
    """Make (homogeneous) linearly separable data."""
    X = RAND.rand(20, 2)
    X[:10, :] += np.array([2, 2])
    X[10:, :] += np.array([-2, -2])
    Y = np.ones(20, dtype=int)
    Y[10:] *= -1
    return X, Y
