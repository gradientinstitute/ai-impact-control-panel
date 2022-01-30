"""A python file that includes unit tests for 'nice_range' function.
Date: 28 Jan 2022
Author: Cindy Chen """
from deva.niceRange import nice_range


def test_rounded():
    """Test normal rounded case."""
    assert(nice_range(1, 14) == (0, 20))


def test_negative():
    """Test the nice range for negative value."""
    assert(nice_range(-4, 90) == (-10, 100))


def test_zero():
    """Test the nice range for 0."""
    assert(nice_range(0, 0) == (-10, 10))


def test_negative_integer():
    """Test on the negative numbers that can be divided by 10."""
    assert(nice_range(-100, -10) == (-110, 0))


def test_decimals():
    """Test on the non-integers."""
    assert(nice_range(13.9, 52.7) == (10, 60))


def test_wrong_order():
    """Test when the min values and the max values
        are not correctly ordered in the input."""
    assert(nice_range(122, 69) == (60, 130))
