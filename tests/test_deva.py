"""Test the eliciters in the DEVA package."""
from deva import elicit
from itertools import permutations
import pickle
import numpy as np
import pytest


def make_data():
    """Make a simple multi-dimensional pareto efficient set with no repeats."""
    data = list(permutations(range(4), 4))
    attribs = [f"X{i+1}" for i in range(4)]

    candidates = [
        elicit.Candidate(chr(65 + i), dict(zip(attribs, row)))
        for i, row in enumerate(data)
    ]

    # information some algorithms assume is available
    scenario = {
        "primary_metric": "X1",
    }
    return candidates, scenario, attribs


@pytest.mark.parametrize("algorithm", elicit.algorithms)
def test_works(algorithm):
    """Test that each algorithm can find the optimum in a toy problem."""
    # Note: assumes choice is from a discrete set (no continuous responses)
    if algorithm == "Enautilus":
        return  # exemption

    candidates, scenario, attribs = make_data()

    # Simulate a linear preference - consistent and easy to discover
    w = np.array([1, 4, 2, 3])

    def oracle(query):
        scores = np.array([[q[a] for a in attribs] for q in query]) @ w
        return query[np.argmin(scores)].name

    best = oracle(candidates)

    eliciter = elicit.algorithms[algorithm](candidates, scenario)

    while not eliciter.terminated():
        ans = oracle(eliciter.query())
        eliciter.put(ans)

    assert eliciter.result().name == best


@pytest.mark.parametrize("algorithm", elicit.algorithms)
def test_pickleable(algorithm):
    """Ensure that each algorithm can be pickled during elicitation."""
    candidates, scenario, attribs = make_data()

    # Run one step of the elicitation so the state is populated
    eliciter = elicit.algorithms[algorithm](candidates, scenario)
    eliciter.put(eliciter.query()[0].name)

    pickle.dumps(eliciter)  # will error if not pickleable
