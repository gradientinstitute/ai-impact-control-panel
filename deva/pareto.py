import numpy as np


def remove_non_pareto(models):
    """Removes all models that are strictly worse than another model."""
    # Check if model is bested by another in every metric
    print("Remove models not on the pareto front")
    non_pareto = []
    for i, m in enumerate(models):
        for r in models:
            if m == r:  # If comparing the model with itself, skip check.
                continue
            # Check which metrics the model is worse at
            worse = np.zeros(len(models[r])).astype(bool)
            for j, met in enumerate(models[m].keys()):
                optimal = models[m][met]['optimal']

                diff =  models[m][met]['score'] - models[r][met]['score']

                if (optimal == 'max') and (diff <= 0):
                    worse[j] = True
                elif (optimal == 'min') and (diff >= 0):
                    worse[j] = True

            # If all are worse, model is not on the pareto front.
            if np.all(worse):
                non_pareto.append(m)
                break

    # Delete all models that aren't on the pareto front
    for m in non_pareto:
        del models[m]

    # Print the number of models deleted
    s = "" if len(non_pareto) == 1 else "s"
    print("Deleted {} model{}.".format(len(non_pareto), s))

    return models
