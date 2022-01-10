"""Productionising LDA.py"""
from numpy.random.mtrand import choice, sample
from deva import fileio
import numpy as np
import matplotlib.pyplot as plt
import plot3d
from deva import interface, elicit, bounds
from bounds_client import tabulate


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
    # sampler = bounds.PlaneSampler(ref, table, sign, attribs, steps=15)  # TODO

    rand_sampler = bounds.LinearRandom(ref, table, sign, attribs, steps=50)
    lg_sampler = bounds.LinearActive(ref, table, sign, attribs, steps=50, epsilon=0.1, n_steps_converge=5)

    def run_bounds_eliciter(sample):
        sampler = sample

        # logged for plotting
        est_weights = []
        true_weights = []

        # For display purposes
        ref_candidate = elicit.Candidate("Baseline", baseline, None)

        print("Do you prefer to answer automatically? Y/N")
        yes = ["Y", "Yes", "y", "yes"]
        answer = input() in yes
        base = ["Baseline", "Base", "baseline", "base"]

        while not sampler.terminated:

            # Display the choice between this and the reference
            interface.text(elicit.Pair(sampler.query, ref_candidate), metrics)
            choices.append(sampler.choice)

            true_weights.append(w_true)
            est_weights.append(sampler.w)

            if answer:
                # Answer automatically
                label = oracle(sampler.choice)
                sampler.observe(label)
            else:
                # Answer based on user's input
                label = input() not in base
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

        errors = [abs(true_weights[i] - est_weights[i]) for i in range(len(true_weights))]
        return errors

    # logged for plotting
    print("You are using LinearRandom Eliciter")
    choices = []
    rand_eliciter = run_bounds_eliciter(rand_sampler)

    # logged for plotting
    print("\n")
    print("You are using LinearActive Eliciter")
    choices = []
    lg_eliciter = np.array(run_bounds_eliciter(lg_sampler))

    # ----------- visualisation --------------
    # plot the error (diff of w_true and w) / the angel changes
    # TODO: compare three eliciters
    # compare two different approaches (LinearActive and LinearRandom)
    sampler = lg_sampler

    # normalise to unit vector
    lg_hat = np.array([lg_eliciter[i] /(lg_eliciter[i]@lg_eliciter[i])**.5 for i in range(len(lg_eliciter))])
    w = np.sum(lg_hat, axis=1)

    rand_hat = np.array([rand_eliciter[i] /(rand_eliciter[i]@rand_eliciter[i])**.5 for i in range(len(rand_eliciter))])
    r = np.sum(rand_hat, axis=1)

    # plot for error rate comparison
    plot1 = plt.figure(1)
    plt.plot(w, label = 'LinearActive')
    plt.plot(r, label = 'LinearRandom')
    plt.ylabel('error rate')
    plt.xlabel('steps')
    plt.suptitle('Eliciters Comparisons')
    plt.legend()


    # Display 'error' plots
    # w0 = list(np.array(lg_eliciter)[:,0])
    # w1 = list(np.array(lg_eliciter)[:,1])
    # w2 = list(np.array(lg_eliciter)[:,2])
    # w = []

    # normalise to unit vector
    # print(w0,w1,w2)
    # w.append(w0)
    # w.append(w1)
    # w.append(w2)    
    # print(w)
    
    # w = np.add(w0_hat, w1_hat, w2_hat)

    # r0 = list(np.array(rand_eliciter)[:,0])
    # r1 = list(np.array(rand_eliciter)[:,1])
    # r2 = list(np.array(rand_eliciter)[:,2])

    # r = np.add(r0_hat, r1_hat, r2_hat)

    # # plot for error rate comparison
    # plot0 = plt.figure(0)
    # plt.plot(w, label = 'LinearActive')
    # plt.plot(r, label = 'LinearRandom')
    # plt.ylabel('error rate')
    # plt.xlabel('steps')
    # plt.legend()


    # TODO: name the plots and y-axis

    # plot0 = plt.figure(0)
    # plt.plot(w0, label = 'LinearActive')
    # plt.plot(r0, label = 'LinearRandom')
    # plt.ylabel('error rate')
    # plt.xlabel('steps')
    # plt.legend()

    # plot1 = plt.figure(1)
    # plt.plot(w1, label = 'LinearActive')
    # plt.plot(r1, label = 'LinearRandom')
    # plt.ylabel('error rate')
    # plt.xlabel('steps')
    # plt.legend()

    # plot2 = plt.figure(2)
    # plt.plot(w2, label = 'LinearActive')
    # plt.plot(r2, label = 'LinearRandom')
    # plt.ylabel('error rate')
    # plt.xlabel('steps')
    # plt.legend()

    print("See sampling plot")

    # Display 3D plot  -------------------------
    plot2 = plt.figure(2)
    plot3d.sample_trajectory(choices, attribs)
    rad = plot3d.radius(choices)[:3]
    plot3d.weight_disc(w_true[:3], ref[:3], rad, 'b', "true boundary")
    plot3d.weight_disc(sampler.w[:3], ref[:3], rad, 'r', "estimated boundary")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
