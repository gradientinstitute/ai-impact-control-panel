"""A python file that includes unit tests for 'nice_range' function.
Date: 28 Jan 2022
Author: Cindy Chen """
from deva.niceRange import nice_range
import unittest


class TestNiceRange(unittest.TestCase):
    """Unit tests for 'nice_range'."""

    def test_rounded(self):
        """Test normal rounded case."""
        self.assertEqual(nice_range(1, 14), (0, 20))

    def test_negative(self):
        """Test the nice range for negative value."""
        self.assertEqual(nice_range(-4, 90), (-10, 100))

    def test_zero(self):
        """Test the nice range for 0."""
        self.assertEqual(nice_range(0, 0), (-10, 10))

    def test_negative_integer(self):
        """Test on the negative numbers that can be divided by 10."""
        self.assertEqual(nice_range(-100, -10), (-110, 0))

    def test_decimals(self):
        """Test on the non-integers."""
        self.assertEqual(nice_range(13.9, 52.7), (10, 60))

    def test_wrong_order(self):
        """Test when the min values and the max values
           are not correctly ordered in the input."""
        self.assertEqual(nice_range(122, 69), (60, 130))


if __name__ == '__main__':
    unittest.main()
