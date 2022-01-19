from deva import elicit
from itertools import permutations
import numpy as np
import pytest

# @pytest.mark.parametrize('algorithm', elicit.algorithms)
def test_works(algorithm):
    data = list(permutations(range(4), 4))  # pareto efficient set
    w = np.arange(1,5)  # hidden weight

    algo = elicit.algorithms[algorithm]


    eliciter = algo(candidates, scenario)
    import smart_embed
    smart_embed.embed(locals(), globals())



# def test_pickleable():
#     assert __version__ == '0.1.0'

if __name__ == "__main__":
    test_works(elicit.Toy)
