"""Module to filter pareto inefficient candidates."""
import numpy as np


def remove_non_pareto(models):
    """Reduces the set of models down to the efficient set."""
    n = len(models)
    dominated = np.zeros(n, dtype=bool)

    names, scores = zip(*models.items())
    # count = 0

    for i, m in enumerate(scores):
        for j, n in enumerate(scores):

            # optional checks to reduce the number of comparisons
            if dominated[i]:
                break

            if dominated[j] | (i == j):
                continue

            dominated[i] |= (all(m[a] >= n[a] for a in m)
                             & any(m[a] > n[a] for a in m))
            # count += 1

    # print(f"Comparisons: {count/len(names)**2:.0%}")
    efficient = models.copy()
    for name, dom in zip(names, dominated):
        if dom:
            del efficient[name]

    d = sum(dominated)
    s = "" if d == 1 else "s"
    print("Deleted {} pareto inefficient model{}.".format(d, s))

    return efficient
