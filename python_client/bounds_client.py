"""Basic client to elicit bounds by talking to the server."""
import requests
import numpy as np
import matplotlib.pyplot as plt
import plot3d
from deva import elicit, interface

# from python_client.nl_bounds import distance, is_below
# from python_client.bounds_local import evaluation

import pickle

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
    meta = scenarios[scenario]
    metrics = meta["metrics"]
    attribs = sorted(metrics)  # canonical order for plotting

    # Create a hidden "ground truth" oracle function
    request = f'http://127.0.0.1:8666/{scenario}/ranges'
    print(request)
    candidates = sess.get(request).json()
    attribs, table = tabulate(candidates, metrics)
    w_true = 0.1 + 0.9 * np.random.rand(len(attribs))
    w_true /= (w_true @ w_true)**.5  # signed unit vector

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
        
        # center = [50, 50]
        # r = 10
        # q = q[:2]
        # def nl_oracle(q):
        #     return np.logical_and((np.array(distance(q, center)) >= r),
        #                           is_below(q, center))

        # label = nl_oracle(q)

        label = ((q - ref) @ w_true < 0)  # oracle!
        data = {}

        if label:
            print(f"Choice: Oracle (ACCEPTED) {left.name}.\n\n")
            data = {"first": left.name, "second": right.name}
        else:
            print(f"Choice: Oracle (REJECTED) {left.name}.\n\n")
            data = {"first": right.name, "second": left.name}

        # Reply to server
        choice = sess.put(request, json=data).json()


    # Terminated - decode the model
    # print(os.path.abspath("."))
    model_ID = sess.get(request).json()
    path = 'server/mlserver/' + model_ID["model_ID"]
    model = pickle.load(open(path, "rb"))  # load the model from disk
    # proba = model.predict_prob
    
    # model = choice['hyperplane']
    # ref = np.array([model['origin'][a] for a in attribs])
    # w_est = np.array([model['normal'][a] for a in attribs])

    # Display text results report
    print("Experimental results ------------------")
    # print("Hidden weights:    ", w_true.round(2))
    # print("Estimated weights: ", w_est.round(2))
    accept = ((table - ref) @ w_true < 0)
    # pred = ((table - ref) @ w_est < 0)
    # pred = proba
    # accept = nl_oracle(table)
    pred = model.guess(table)
    accept_rt = accept.mean()
    acc = np.mean(accept == pred)
    print(f"True preference would accept {accept_rt:.0%} of real candidates.")
    print(f"Model predicted oracle with {acc:.0%} accuracy.")
    print("<< see sampling plot for visualisation >>")

    # Display 3D plot  -------------------------
    # because this is display, we need to flip choices
    # sign = np.array([1 if metrics[a].get('lowerIsBetter', True) else -1
    #                 for a in attribs])

    # plot3d.sample_trajectory(choice_log * sign, attribs)
    # rad = plot3d.radius(choice_log)[:3]
    # plot3d.weight_disc(
    #     w_true[:3], (ref * sign)[:3], rad, 'b', "true boundary")
    # plot3d.weight_disc(
    #     w_est[:3], (ref * sign)[:3], rad, 'r', "estimated boundary")
    # plt.legend()
    # plt.show()


def tabulate(candidates, metrics):
    """Convert dict candidates to arrays."""
    attribs = sorted(metrics)
    table = np.zeros((len(candidates), len(attribs)))

    for i, c in enumerate(candidates):
        table[i, :] = [c[a] for a in attribs]

    return attribs, table


# def distance(a, center):
#     a = np.array(a)
#     center = np.array(center)
#     dist = np.sqrt(np.sum((a - center) ** 2, axis=-1))
#     return dist


# def is_below(q, center):
#     # Check whether a point is below a straight line through the center
#     q = np.array(q)
#     if q.ndim == 1:
#         x = q[0]
#         y = q[1]
#     else:
#         x = q[:, 0]
#         y = q[:, 1]
#     b = np.sum(center)
#     y_max = -x + b

#     return y <= y_max


if __name__ == "__main__":
    main()
