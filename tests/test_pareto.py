"""
Test the code to remove non-pareto-efficient candidates.

Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
"""
from deva.pareto import remove_non_pareto
from itertools import product


def test_pareto():
    """Test that the pareto filter works on a toy problem."""
    dims = 4
    all_permutations = product(*[range(dims)] * dims)
    cands = [v for v in all_permutations if sum(v) >= 6]

    atts = ["a", "b", "c", "d"]
    models = {str(i): dict(zip(atts, v)) for i, v in enumerate(cands)}

    eff = remove_non_pareto(models)
    ans = {k: v for k, v in models.items() if sum(v.values()) == 6}

    assert ans == eff


if __name__ == "__main__":
    test_pareto()
