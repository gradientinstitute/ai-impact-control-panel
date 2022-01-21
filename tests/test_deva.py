from deva import elicit
from itertools import permutations
import pickle
import numpy as np
import pytest


def make_data():
    data = list(permutations(range(4), 4))  # pareto efficient set
    attribs = [f"X{i+1}" for i in range(4)]

    candidates = [
        elicit.Candidate(chr(65+i), dict(zip(attribs, row)))
        for i, row in enumerate(data)
    ]

    # information some algorithms assume is available
    scenario = {
        "primary_metric": "X1",
    }
    return candidates, scenario, attribs


@pytest.mark.parametrize('algorithm', elicit.algorithms)
def test_works(algorithm):

    candidates, scenario, attribs = make_data()
    # Simulate a linear preference - consistent and easy to discover
    w = np.array([1, 4, 2, 3])

    def oracle(query):
        vals = np.array([[q[a] for a in attribs] for q in eliciter.query])
        scores = vals @ w
        if (scores[0] <= scores[1]):
            return query[0].name
        else:
            return query[1].name

    scores = np.array([[q[a] for a in attribs] for q in candidates]) @ w
    best = np.argmin(scores)

    eliciter = elicit.algorithms[algorithm](candidates, scenario)

    while not eliciter.terminated:
        ans = oracle(eliciter.query)
        eliciter.input(ans)
    # run one step (not to convergence)

    choice = eliciter.result.name
    ref = candidates[best].name

    assert choice == ref


@pytest.mark.parametrize('algorithm', elicit.algorithms)
def test_pickleable(algorithm):

    candidates, scenario, attribs = make_data()

    # Run one step of the elicitation so the state is populated
    eliciter = elicit.algorithms[algorithm](candidates, scenario)
    eliciter.input(eliciter.query[0].name)

    pickle.dumps(eliciter)  # will error if not pickleable
