from deva.niceRange import nice_range
import unittest


class TestNiceRange(unittest.TestCase):
    def test_rounded(self):
        self.assertEqual(nice_range(1, 14), (0, 20))

    def test_negative(self):
        self.assertEqual(nice_range(-4, 90), (-10, 100))

    def test_zero(self):
        self.assertEqual(nice_range(0, 0), (-10, 10))

    def test_negative_whole(self):
        self.assertEqual(nice_range(-100, -10), (-110, 0))

    def test_decimals(self):
        self.assertEqual(nice_range(13.9, 52.7), (10, 60))

    def test_wrong_order(self):
        self.assertEqual(nice_range(122, 69), (60, 130))


if __name__ == '__main__':
    unittest.main()
