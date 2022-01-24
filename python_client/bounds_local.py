"""Productionising LDA.py"""
from deva import fileio
import numpy as np
import matplotlib.pyplot as plt
import plot3d
from deva import interface, elicit, bounds
from bounds_client import tabulate

# from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss


def main():
    np.random.seed(42)

    # Load candidates and metadata
    scenario = "jobs"
    candidates, meta = fileio.load_scenario(scenario)
    metrics = meta["metrics"]
    attribs, table = tabulate(candidates, metrics)

    # [Optionally] truncate for testing
    attribs = attribs[:3]
    table = table[:, :3]

    # Load baseline for comparison
    baseline = meta["baseline"]
    ref = np.array([baseline[a] for a in attribs])
    ref = ref[:3]

    # logged for plotting
    eli_choices = {}  # a dict storing the choices for each eliciter
    eli_scores = {}  # storing the average 'log loss' for each eliciter
    eli_errors = {}  # storing the error rate for each eliciter

    n_iter = 0
    max_iter = 5
    # A loop to reduce variance due to initial conditions
    while n_iter < max_iter:
        # Test whether the sampler can elicit this oracle's preference
        eliciters = {
            "PlaneSampler": bounds.PlaneSampler(ref, table, attribs, steps=50),
            "LinearRandom": bounds.LinearRandom(ref, table, attribs, steps=50),
            "LinearActive": bounds.LinearActive(ref, table, attribs, steps=50,
                                                epsilon=0.05,
                                                n_steps_converge=5)
        }

        # Create a hidden "ground truth" oracle function
        dims = len(ref)
        w_true = 0.1 + 0.9 * np.random.rand(dims)  # positive
        w_true /= (w_true @ w_true)**.5  # signed unit vector

        def oracle(q):
            return ((q - ref) @ w_true < 0)

        for eliciter in eliciters:
            samp_name = eliciter
            print(f'You are using {samp_name} Eliciter\n')
            outputs = run_bounds_eliciter(eliciters[eliciter], metrics, table,
                                          baseline, w_true, oracle, ref,
                                          n_samples=100)
            (sample_choices, est_w, scores) = outputs

            if n_iter == 0:
                eli_scores[samp_name] = []
            else:
                eli_scores[samp_name].append(scores)
            if n_iter == max_iter-1:
                eli_choices[samp_name] = sample_choices
                eli_errors[samp_name] = compare_weights(w_true, est_w)
        n_iter += 1

    # ----------- visualisation --------------
    # compare three eliciters
    plt.figure(0)
    for k in eli_errors:
        plt.plot(eli_errors[k], label=k)
    plt.ylabel('error rate')
    plt.xlabel('steps')
    plt.suptitle('Eliciters Comparison')
    plt.legend()

    avg_scores = {}
    for e in eliciters:
        min_step = min(map(len, eli_scores[e]))
        avg_scores[e] = np.array([i[:min_step] for i in eli_scores[e]])
        avg_scores[e] = np.mean(avg_scores[e], axis=0)

    plt.figure(1)
    for k in eli_scores:
        plt.plot(np.array(avg_scores[k]), label=k)
    plt.ylabel('log loss')
    plt.xlabel('steps')
    plt.suptitle('Eliciters Comparison')
    plt.legend()

    print("See sampling plot")

    # only shows the 3D plot for LinearActive Eliciter
    sampler = eliciters["LinearActive"]
    choices = eli_choices["LinearActive"]

    # Display 3D plot  -------------------------
    plt.figure(2)
    sign = np.array([1 if metrics[a].get('lowerIsBetter', True) else -1
                    for a in attribs])

    plot3d.sample_trajectory(choices * sign, attribs)
    rad = plot3d.radius(choices)[:3]
    plot3d.weight_disc(
        w_true[:3], (ref * sign)[:3], rad, 'b', "true boundary")
    plot3d.weight_disc(
        sampler.w[:3], (ref * sign)[:3], rad, 'r', "estimated boundary")
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

        # Display the choice between this and the reference
        interface.text((sampler.query, ref_candidate), metrics)
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
