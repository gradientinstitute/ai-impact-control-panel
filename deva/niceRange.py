import math
import unittest


def nice_range(min, max):
    # round min down & max up to nearest the 10
    div = 10
    if min % div == 0:
        min -= div
    if max % div == 0:
        max += div
    min = math.floor(min / div) * div
    max = math.ceil(max / div) * div
    return (min, max)


class TestNiceRange(unittest.TestCase):
    def test_1(self):
        self.assertEqual(nice_range(-4, 90), (-10, 100))

    def test_2(self):
        self.assertEqual(nice_range(1, 14), (0, 20))

    def test_3(self):
        self.assertEqual(nice_range(0, 2), (-10, 10))

    def test_4(self):
        self.assertEqual(nice_range(-100, -10), (-110, 0))


if __name__ == '__main__':
    unittest.main()
