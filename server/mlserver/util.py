"""Module supporting DEVA flask server."""
from flask import jsonify as _jsonify
import random
import string
import numpy as np


def round_floats(o):
    """Recursively round floats pre-json."""
    if isinstance(o, float):
        return round(o, 3)
    elif isinstance(o, dict):
        return {k: round_floats(v) for k, v in o.items()}
    elif isinstance(o, (list, tuple, np.ndarray)):
        return [round_floats(x) for x in o]
    return o


def jsonify(o):
    """Apply flask's jsonify with some float formatting."""
    return _jsonify(round_floats(o))


def random_key(n, exclude=()):
    """Make a random string of n characters."""
    while True:
        key = "".join(random.choice(string.ascii_letters) for i in range(n))
        if key not in exclude:
            break

    return key
