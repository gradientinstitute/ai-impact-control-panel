"""Non-linear bounds experiment."""
import numpy as np
import matplotlib.pyplot as plt
from deva import bounds  # , interface, elicit
# from bounds_client import tabulate

from python_client.bounds_local import evaluation


def main():
    """Non-linear bounds experiment."""
    np.random.seed(42)

    # Define nonlinear scenario
    attribs = ["attr1", "attr2"]
    ref = [50, 50]
    u = np.arange(0, 100, 1)
    v = np.arange(0, 100, 2)

    candidates = []

    for i in range(len(u)):
        for j in range(len(v)):
            candidates.append([u[i], v[j]])

    table = np.array(candidates)

    # logged for plotting
    eli_choices = {}  # a dict storing the choices for each eliciter
    eli_scores = {}  # storing the average "log loss" for each eliciter

    n_iter = 0
    max_iter = 5
    # A loop to reduce variance due to initial conditions
    while n_iter < max_iter:
        # Test whether the sampler can elicit this oracle's preference
        eliciters = {
            "PlaneSampler": bounds.PlaneSampler(ref, table, attribs, steps=50),
            "LinearRandom": bounds.LinearRandom(ref, table, attribs, steps=50),
            "LinearActive": bounds.LinearActive(ref, table, attribs, steps=50,
                                                epsilon=0.005,
                                                n_steps_converge=5),
            "Active": bounds.KNeighborsEliciter(ref, table, attribs, steps=100)
        }

        # Create a non-linear oracle function
        r = 10  # radius
        center = ref

        def nl_oracle(q):
            return np.logical_and((np.array(bounds.distance(q, center)) >= r),
                                  bounds.is_below(q, center))

        for eliciter in eliciters:
            samp_name = eliciter
            print(f"You are using {samp_name} Eliciter\n")
            outputs = run_bounds_eliciter(eliciters[eliciter], table,
                                          nl_oracle, ref,
                                          n_samples=100)
            (sample_choices, scores) = outputs

            if n_iter == 0:
                eli_scores[samp_name] = []
            else:
                eli_scores[samp_name].append(scores)
            if n_iter == max_iter - 1:
                eli_choices[samp_name] = sample_choices
        n_iter += 1

    # ----------- visualisation --------------
    sampler = eliciters["Active"]
    choices = eli_choices["Active"]
    # Display 2D plot for nl_oracle
    plot_nl_bound(sampler, choices, nl_oracle)


def plot_nl_bound(sampler, choices, nl_oracle):
    """Display 2D plot for nl_oracle"""
    labels = nl_oracle(choices)

    # Create an instance of Logistic Regression Classifier and fit the data.
    X = choices
    Y = labels

    # Plot the decision boundary.
    x_min, x_max = 20, 80
    y_min, y_max = 20, 80
    h = 100  # number of samples
    xx, yy = np.meshgrid(np.linspace(x_min, x_max, h),
                         np.linspace(y_min, y_max, h))
    Z = nl_oracle(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.figure()
    plt.contourf(xx, yy, Z, levels=[0, 0.5, 1], cmap=plt.cm.Spectral)
    plt.colorbar()

    # Plot the true boundary
    Z = sampler.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
    Z = Z.reshape(xx.shape)
    CS = plt.contour(xx, yy, Z, levels=[.25, .5, .75], cmap="RdYlGn")
    plt.clabel(CS, CS.levels, inline=True, fontsize=10)

    # Plot also the training points
    plt.scatter(X[:, 0], X[:, 1], c=Y, edgecolors="k", cmap=plt.cm.Spectral)
    plt.xlabel("attr1")
    plt.ylabel("attr2")

    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())

    plt.show()


def run_bounds_eliciter(sample, table, oracle, ref, n_samples):
    """Run a bounds eliciter to termination."""
    sampler = sample

    # logged for plotting
    choices = []
    scores = []  # log_loss for each step
    step = 0

    answer = True
    base = ["baseline", "base"]

    while not sampler.terminated():
        step += 1

        choices.append(sampler.choice)

        if answer:
            # Answer automatically
            label = oracle(sampler.choice)

        else:
            # Answer based on user's input
            label = input().lower() not in base

        sampler.put(label)

        if label:
            print("Choice: Oracle (ACCEPTED) candidate.\n\n")
        else:
            print("Choice: Oracle (REJECTED) candidate.\n\n")

        if step >= 10:
            score = evaluation(sampler, ref, n_samples, oracle)
            scores.append(score)

    # Display text results report
    print("Experimental results ------------------")
    accept = oracle(table)
    accept_rt = accept.mean()
    pred = sampler.predict(table)
    acc = np.mean(accept == pred)
    print(f"True preference would accept {accept_rt:.0%}\
            of real candidates.")
    print(f"Candidates labeled with {acc:.0%} accuracy.")

    return (np.array(choices), scores)


if __name__ == "__main__":
    main()
