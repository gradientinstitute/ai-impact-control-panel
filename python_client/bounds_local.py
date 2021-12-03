"""Productionising LDA.py"""
from deva import fileio
import numpy as np
import matplotlib.pyplot as plt
import plot3d
from deva import interface, elicit, bounds


def main():
    np.random.seed(42)

    # Load candidates and metadata
    scenario = "jobs"
    candidates, meta = fileio.load_scenario(scenario)
    metrics = meta["metrics"]

    # Encode candidates and "higherIsBetter" as arrays
    attribs, table, sign = bounds.tabulate(candidates, metrics)

    # Load baseline for comparison
    baseline = fileio.load_baseline(scenario)
    ref = np.array([baseline[a] for a in attribs])

    # Create a hidden "ground truth" oracle function
    dims = len(ref)
    w_true = 0.1 + 0.9 * np.random.rand(dims)  # positive
    w_true *= sign / (w_true @ w_true)**.5  # signed unit vector

    def oracle(q):
        return ((q - ref) @ w_true < 0)

    # Test whether the sampler can elicit this oracle's preference
    sampler = bounds.TestSampler(ref, table, sign, attribs, steps=15)
    choices = []  # logged for plotting

    # For display purposes
    ref_candidate = elicit.Candidate("Baseline", baseline, None)

    while not sampler.terminated:

        # Display the choice between this and the reference
        interface.text(elicit.Pair(sampler.query, ref_candidate), metrics)

        # Answer automatically
        choices.append(sampler.choice)
        label = oracle(sampler.choice)
        sampler.observe(label)

        if label:
            print("Choice: Oracle (ACCEPTED) candidate.\n\n")
        else:
            print("Choice: Oracle (REJECTED) candidate.\n\n")

    # Display text results report
    print("Experimental results ------------------")
    print("Truth:    ", w_true)
    print("Estimate: ", sampler.w)
    accept = oracle(table)
    accept_rt = accept.mean()
    pred = sampler.guess(table)
    acc = np.mean(accept == pred)
    print(f"True preference would accept {accept_rt:.0%} of real candidates.")
    print(f"Candidates labeled with {acc:.0%} accuracy.")
    print("See sampling plot")

    # Display 3D plot  -------------------------
    plot3d.sample_trajectory(choices, attribs)
    rad = plot3d.radius(choices)[:3]
    plot3d.weight_disc(w_true[:3], ref[:3], rad, 'b', "true boundary")
    plot3d.weight_disc(sampler.w[:3], ref[:3], rad, 'r', "estimated boundary")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
