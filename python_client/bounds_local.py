"""Productionising LDA.py"""
from deva import fileio
import numpy as np
import matplotlib.pyplot as plt
import plot3d
from deva import interface, elicit, bounds
from bounds_client import tabulate

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss


def main():
    np.random.seed(42)

    # Load candidates and metadata
    scenario = "jobs"
    candidates, meta = fileio.load_scenario(scenario)
    metrics = meta["metrics"]

    # Encode candidates and "higherIsBetter" as arrays
    attribs, table, sign = tabulate(candidates, metrics)

    # We can only plot in 3 dimensions... drop the later ones
    attribs = attribs[:3]
    table = table[:, :3]
    sign = sign[:3]

    # Load baseline for comparison
    baseline = fileio.load_baseline(scenario)
    ref = np.array([baseline[a] for a in attribs])
    ref = ref[:3]

    # Create a hidden "ground truth" oracle function
    dims = len(ref)
    w_true = 0.1 + 0.9 * np.random.rand(dims)  # positive
    w_true *= sign / (w_true @ w_true)**.5  # signed unit vector

    def oracle(q):
        return ((q - ref) @ w_true < 0)

    # Test whether the sampler can elicit this oracle's preference

    plane_sampler = bounds.PlaneSampler(ref, table, sign, attribs, steps=50)
    linear_random = bounds.LinearRandom(ref, table, sign, attribs, steps=50)
    linear_active = bounds.LinearActive(ref, table, sign, attribs, steps=50,
                                        epsilon=0.05, n_steps_converge=5)

    # ----------- visualisation --------------
    # compare three eliciters

    eliciters = [plane_sampler, linear_random, linear_active]
    eli_names = {plane_sampler: "PlaneSampler", linear_random: "LinearRandom",
                 linear_active: "LinearActive"}
    eli_choices = {}  # a dictionary storing the choices for each eliciter
    eli_scores = {}  # a dictionary storing the 'log loss' for each eliciter

    plt.figure(0)

    for eliciter in eliciters:
        samp_name = eli_names[eliciter]
        print(f'You are using {samp_name} Eliciter\n')
        outputs = run_bounds_eliciter(eliciter, metrics, table, baseline,
                                      w_true, oracle, ref, n_samples=100)
        (sample_choices, est_w, scores) = outputs
        eli_choices[samp_name] = sample_choices

        eli_scores[samp_name] = scores

        w = compare_weights(w_true, est_w)
        plt.plot(w, label=f'{samp_name}')

    plt.ylabel('error rate')
    plt.xlabel('steps')
    plt.suptitle('Eliciters Comparison')
    plt.legend()

    plt.figure(1)
    for k in eli_scores:
        plt.plot(np.array(eli_scores[k])[:, 0], np.array(eli_scores[k])[:, 1],
                 label=f'{k}')
    plt.ylabel('log loss')
    plt.xlabel('steps')
    plt.suptitle('Eliciters Comparison')
    plt.legend()

    print("See sampling plot")

    # only shows the 3D plot for LinearActive Eliciter
    sampler = linear_active
    choices = eli_choices["LinearActive"]

    # Display 3D plot  -------------------------
    plt.figure(2)
    plot3d.sample_trajectory(choices, attribs)
    rad = plot3d.radius(choices)[:3]
    plot3d.weight_disc(w_true[:3], ref[:3], rad, 'b', "true boundary")
    plot3d.weight_disc(sampler.w[:3], ref[:3], rad, 'r', "estimated boundary")
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
    yes = ["y", "yes"]
    answer = input().lower() in yes
    base = ["baseline", "base"]

    while not sampler.terminated:
        step += 1

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
            score = evaluation(choices, ref, n_samples, oracle)
            scores.append((step, score))

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


def evaluation(choices, ref, n_samples, oracle, tests_per_steps=50):
    lr = LogisticRegression()

    train_X = choices
    train_y = [oracle(x) for x in train_X]
    lr.fit(train_X, train_y)

    loss = 0

    # averaging the log_loss over multiple tests per steps
    for _ in range(tests_per_steps):
        # generate random testing data
        test_X = random_choice(ref, n_samples)
        test_y = [oracle(x) for x in test_X]  # y_true
        probabilities = lr.predict_proba(test_X)  # y_pred
        loss += log_loss(test_y, probabilities)

    avg_loss = loss / tests_per_steps

    return avg_loss  # lower is better


def random_choice(ref, n_samples):
    rand = np.random.random_sample((n_samples, len(ref))) * 10
    sign = np.random.choice([-1, 1])
    choice = sign * rand + ref

    return choice


if __name__ == "__main__":
    main()
