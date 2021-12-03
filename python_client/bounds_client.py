"""Productionising bounds eliciter demo to talk to server."""
import requests
import numpy as np
import matplotlib.pyplot as plt
import plot3d
from deva import interface, elicit


def tabulate(candidates, metrics):
    attribs = sorted(metrics)
    table = np.zeros((len(candidates), len(attribs)))
    for i, c in enumerate(candidates):
        table[i, :] = [c[a] for a in attribs]

    sign = np.array([-1 if metrics[a]["higherIsBetter"] else 1
                     for a in attribs])

    return attribs, table, sign



def main():
    sess = requests.Session()

    print("Requesting Scenario List")
    request = 'http://127.0.0.1:8666/scenarios'
    print(request)
    scenarios = sess.get(request).json()
    scenario = "jobs"

    while scenario not in scenarios:
        print("Please choose from: " + ", ".join(scenarios.keys()))
        scenario = input() or "!!!"

    # Extract the metadata from the list for display purposes
    metrics = scenarios[scenario]["metrics"]
    attribs = sorted(metrics)  # canonical order for plotting

    # Create a hidden "ground truth" oracle function
    request = f'http://127.0.0.1:8666/{scenario}/ranges'
    print(request)
    candidates = sess.get(request).json()
    attribs, table, sign = tabulate(candidates, metrics)
    w_true = 0.1 + 0.9 * np.random.rand(len(attribs))
    w_true *= sign / (w_true @ w_true)**.5  # signed unit vector

    # Create a bounds session
    print("Starting eliciter session")
    request = f'http://127.0.0.1:8666/{scenario}/bounds/init'
    sess.put(request)
    print(request)

    # log the query choice_log for plotting later
    choice_log = []

    request = f'http://127.0.0.1:8666/{scenario}/bounds/choice'
    print(request)
    choice = sess.get(request).json()

    while True:

        if "left" not in choice:
            break

        # Display the choice between this and the reference
        left = elicit.Candidate(
            choice["left"]["name"],
            choice["left"]["values"],
        )
        right = elicit.Candidate(
            choice["right"]["name"],
            choice["right"]["values"],
        )
        interface.text(elicit.Pair(left, right), metrics)

        # Answer automatically
        q = np.array([left.attributes[a] for a in attribs])
        ref = np.array([right.attributes[a] for a in attribs])

        choice_log.append(q)
        label = ((q - ref) @ w_true < 0)  # oracle!
        data = {}

        if label:
            print("Choice: Oracle (ACCEPTED) candidate.\n\n")
            data = {"first": left.name, "second": right.name}
        else:
            print("Choice: Oracle (REJECTED) candidate.\n\n")
            data = {"first": right.name, "second": left.name}

        # Reply to server
        choice = sess.put(request, json=data).json()


    # Terminated - decode the model
    model = choice['hyperplane']
    ref = np.array([model['origin'][a] for a in attribs])
    w_est = np.array([model['normal'][a] for a in attribs])

    # Display text results report
    print("Experimental results ------------------")
    print("Truth:    ", w_true)
    print("Estimate: ", w_est)
    accept = ((table - ref) @ w_true < 0)
    pred = ((table - ref) @ w_est < 0)
    accept_rt = accept.mean()
    acc = np.mean(accept == pred)
    print(f"True preference would accept {accept_rt:.0%} of real candidates.")
    print(f"Candidates labeled with {acc:.0%} accuracy.")
    print("See sampling plot")

    # Display 3D plot  -------------------------
    plot3d.sample_trajectory(choice_log, attribs)
    rad = plot3d.radius(choice_log)[:3]
    plot3d.weight_disc(w_true[:3], ref[:3], rad, 'b', "true boundary")
    plot3d.weight_disc(w_est[:3], ref[:3], rad, 'r', "estimated boundary")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
