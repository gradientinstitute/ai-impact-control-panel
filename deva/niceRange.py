"""A python file which includes 'nice_range' function
that can be used as a helper function in fileio.py
Date: Jan 28, 2022
Author: Muyao Chen """
import math


def nice_range(a, b):
    """Round min down and max up to nearest the 10"""
    min_num = min(a, b)
    max_num = max(a, b)
    div = 10
    if min_num % div == 0:
        min_num -= div
    if max_num % div == 0:
        max_num += div
    min_num = math.floor(min_num / div) * div
    max_num = math.ceil(max_num / div) * div
    return (min_num, max_num)
