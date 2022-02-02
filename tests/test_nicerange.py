"""
Unit tests for estimating a bounds range from data.

Date: 28 Jan 2022
Author: Cindy Chen
"""
from deva.nice_range import nice_range


def test_rounded():
    """Test normal rounded case."""
    assert(nice_range(1, 14, 10) == (0, 20))


def test_negative():
    """Test the nice range for negative value."""
    assert(nice_range(-4, 90, 10) == (-10, 100))


def test_zero():
    """Test the nice range for 0."""
    assert(nice_range(0, 0, 1) == (-1, 1))


def test_negative_integer():
    """Test on the negative numbers that can be divided by 100."""
    assert(nice_range(-100, -10, 100) == (-200, 0))


def test_decimals():
    """Test on the non-integers."""
    assert(nice_range(13.9, 52.7, 10) == (10, 60))


def test_wrong_order():
    """Test handling of min and max being out of order."""
    assert(nice_range(122, 69, 100) == (0, 200))


def test_true_range():
    """Test on true ranges."""
    assert(nice_range(0, 3872, 1000) == (-1000, 4000))
    assert(nice_range(0, 3910, 1000) == (-1000, 4000))
