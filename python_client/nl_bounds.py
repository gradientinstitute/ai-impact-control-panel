"""Productionising LDA.py"""
import numpy as np
import matplotlib.pyplot as plt
from deva import interface, elicit  # , bounds
# from bounds_client import tabulate

from sklearn.metrics import log_loss


def main():
    np.random.seed(42)

    # TODO: define nonlinear scenario
    # attribs = ["attr1", "attr2"]

    # Create a non-linear oracle function
    r = 20  # radius
    center = [50, 50]

    def distance(a, center):
        a = np.array(a)
        center = np.array(center)

        d = np.sqrt(np.sum((a - center) ** 2, axis=-1))

        return d

    def nl_oracle(q):
        return (np.array(distance(q, center)) <= r)

    # ----------- visualisation --------------
    choices = -100 * np.random.random_sample((1000, 2)) + 100  # TODO

    # Display 2D plot for nl_oracle ------------
    labels = nl_oracle(np.array(choices))
    accept = []
    reject = []

    for i in range(len(labels)):
        if labels[i]:
            accept.append(choices[i])
        else:
            reject.append(choices[i])

    print(len(choices), len(labels))
    print(len(accept), len(reject))

    # accept
    x = np.array(accept)[:, 0]
    y = np.array(accept)[:, 1]

    # reject
    a = np.array(reject)[:, 0]
    b = np.array(reject)[:, 1]

    plt.figure()

    plt.scatter(x, y, color='g',
                marker='o', label="accept")
    plt.scatter(a, b, color='r',
                marker='x', label="reject")
    # plt.xlabel(attribs[0])
    # plt.ylabel(attribs[1])

    # TODO draw boundary (make a grid, evaluate oracle on grid, radius)
    # plot truth (circle)
    # plot estimate boundary (query hasnt asked points) (line? <- logreg)

    plt.legend()
    plt.show()


def run_bounds_eliciter(sample, metrics, table, baseline, w_true, oracle,
                        ref, n_samples):
    sampler = sample

    # logged for plotting
    est_weights = []
    choices = []
    scores = []  # log_loss for each step
    step = 0

    # For display purposes
    ref_candidate = elicit.Candidate("Baseline", baseline, None)

    print("Do you prefer to answer automatically? y/N")
    # matching user inputs
    # yes = ["y", "yes"]
    # answer = input().lower() in yes
    answer = True
    base = ["baseline", "base"]

    while not sampler.terminated:
        step += 1

        # TODO: only asking "Would you accept system_X?"

        # Display the choice between this and the reference
        interface.text(elicit.Pair(sampler.query, ref_candidate), metrics)
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
    print("Truth:    ", w_true)
    print("Estimate: ", sampler.w)
    accept = oracle(table)
    accept_rt = accept.mean()
    pred = sampler.guess(table)
    acc = np.mean(accept == pred)
    print(f"True preference would accept {accept_rt:.0%}\
            of real candidates.")
    print(f"Candidates labeled with {acc:.0%} accuracy.")

    return (choices, np.array(est_weights), scores)


def compare_weights(w_true, est_w):
    # normalise to unit vector
    true_hat = np.array(w_true / (w_true @ w_true)**.5)
    est_hat = np.array([est_w[i] / (est_w[i] @ est_w[i])**.5
                        for i in range(len(est_w))])
    errors = np.abs(np.array(true_hat) - np.array(est_hat))
    error_sum = np.sum(errors, axis=1)
    return error_sum


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
