"""
Compute brackets around data values.

Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
"""

import math


def nice_range(a, b):
    """
    Round min down and max up to the nearest `div`.

    Return the minimum value and the maximum value in order in a tuple.
    """
    min_num = min(a, b)
    max_num = max(a, b)
    diff = math.ceil(max_num - min_num)
    div = 10**(len(str(diff)) - 1)

    if min_num % div == 0:
        min_num -= div
    if max_num % div == 0:
        max_num += div
    min_num = math.floor(min_num / div) * div
    max_num = math.ceil(max_num / div) * div
    return (min_num, max_num)
