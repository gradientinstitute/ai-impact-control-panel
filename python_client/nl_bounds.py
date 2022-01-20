"""Productionising LDA.py"""
import numpy as np
import matplotlib.pyplot as plt
from deva import bounds  # , interface, elicit
# from bounds_client import tabulate

from sklearn.metrics import log_loss
# from sklearn.linear_model import LogisticRegression


def main():
    np.random.seed(42)

    # TODO: define nonlinear scenario
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
    eli_scores = {}  # storing the average 'log loss' for each eliciter

    n_iter = 0
    max_iter = 2
    # A loop to reduce variance due to initial conditions
    while n_iter < max_iter:
        # Test whether the sampler can elicit this oracle's preference
        eliciters = {
            "PlaneSampler": bounds.PlaneSampler(ref, table, attribs, steps=50),
            "LinearRandom": bounds.LinearRandom(ref, table, attribs, steps=50),
            "LinearActive": bounds.LinearActive(ref, table, attribs, steps=50,
                                                epsilon=0.005,
                                                n_steps_converge=5)
        }

        # Create a non-linear oracle function
        r = 10  # radius
        center = [50, 50]

        def distance(a, center):
            a = np.array(a)
            center = np.array(center)
            dist = np.sqrt(np.sum((a - center) ** 2, axis=-1))
            return dist

        def lower_is_better(q):
            q = np.array(q)
            if q.ndim == 1:
                x = q[0]
                y = q[1]
            else:
                x = q[:, 0]
                y = q[:, 1]
            b = np.sum(center)
            y_max = -x + b

            return y <= y_max

        def nl_oracle(q):
            return np.logical_and((np.array(distance(q, center)) >= r),
                                  lower_is_better(q))

        for eliciter in eliciters:
            samp_name = eliciter
            print(f'You are using {samp_name} Eliciter\n')
            outputs = run_bounds_eliciter(eliciters[eliciter], table,
                                          nl_oracle, ref,
                                          n_samples=100)
            (sample_choices, _, scores) = outputs

            if n_iter == 0:
                eli_scores[samp_name] = []
            else:
                eli_scores[samp_name].append(scores)
            if n_iter == max_iter-1:
                eli_choices[samp_name] = sample_choices
        n_iter += 1

    # ----------- visualisation --------------
    sampler = eliciters["LinearRandom"]
    choices = eli_choices["LinearRandom"]

    # Display 2D plot for nl_oracle ------------
    labels = nl_oracle(np.array(choices))

    # Create an instance of Logistic Regression Classifier and fit the data.
    X = np.array(choices)
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
    print(Z.shape)
    plt.figure()
    plt.contourf(xx, yy, Z, levels=[0, 0.5, 1], cmap=plt.cm.Spectral)
    plt.colorbar()

    # Plot the true boundary
    Z = sampler.predict_prob(np.c_[xx.ravel(), yy.ravel()])[:, 1]
    Z = Z.reshape(xx.shape)
    print(Z.shape)
    plt.contour(xx, yy, Z, cmap="jet")
    plt.colorbar()

    # Plot also the training points
    plt.scatter(X[:, 0], X[:, 1], c=Y, edgecolors="k", cmap=plt.cm.Spectral)
    plt.xlabel("x")
    plt.ylabel("y")

    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())

    plt.show()


def run_bounds_eliciter(sample, table, oracle,
                        ref, n_samples):
    sampler = sample

    # logged for plotting
    est_weights = []
    choices = []
    scores = []  # log_loss for each step
    step = 0

    # For display purposes
    # ref_candidate = elicit.Candidate("Baseline", baseline, None)

    print("Do you prefer to answer automatically? y/N")
    # matching user inputs
    # yes = ["y", "yes"]
    # answer = input().lower() in yes
    answer = True
    base = ["baseline", "base"]

    while not sampler.terminated:
        step += 1

        choices.append(sampler.choice)

        est_weights.append(sampler.w)

        if answer:
            # Answer automatically
            label = oracle(sampler.choice)
            sampler.observe(label)

        else:
            # Answer based on user's input
            label = input().lower() not in base
            sampler.observe(label)

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
    pred = sampler.guess(table)
    acc = np.mean(accept == pred)
    print(f"True preference would accept {accept_rt:.0%}\
            of real candidates.")
    print(f"Candidates labeled with {acc:.0%} accuracy.")

    return (choices, np.array(est_weights), scores)


def evaluation(eliciter, ref, n_samples, oracle):
    # generate random testing data
    test_X = random_choice(ref, n_samples)
    test_y = [oracle(x) for x in test_X]  # y_true

    probabilities = eliciter.predict_prob(test_X)  # y_pred

    loss = log_loss(test_y, probabilities, labels=[True, False])

    return loss  # lower is better


def random_choice(ref, n_samples):
    rand = np.random.random_sample((n_samples, len(ref))) * 10
    sign = np.random.choice([-1, 1])
    choice = sign * rand + ref

    return choice


if __name__ == "__main__":
    main()
