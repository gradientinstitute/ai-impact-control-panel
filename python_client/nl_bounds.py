"""Productionising LDA.py"""
import numpy as np
import matplotlib.pyplot as plt
from deva import interface, elicit, bounds
# from bounds_client import tabulate

from sklearn.metrics import log_loss
from sklearn.linear_model import LogisticRegression

def main():
    np.random.seed(42)

    # TODO: define nonlinear scenario
    # attribs = ["attr1", "attr2"]
    # ref = [50, 50]

    # u = np.arange(0, 100, 1)
    # v = np.arange(0, 100, 2)

    # # print(U.shape, V.shape)
    # candidates = []

    # for i in range(len(u)):
    #     for j in range(len(v)):
    #         candidates.append([u[i], v[j]])

    # table = np.array(candidates)  # TODO: 2d array
    # # metrics = []

    # # logged for plotting
    # eli_choices = {}  # a dict storing the choices for each eliciter
    # eli_scores = {}  # storing the average 'log loss' for each eliciter

    # n_iter = 0
    # max_iter = 2
    # # A loop to reduce variance due to initial conditions
    # while n_iter < max_iter:
    #     # Test whether the sampler can elicit this oracle's preference
    #     eliciters = {
    #         # "PlaneSampler": bounds.PlaneSampler(ref, table, attribs, steps=50),
    #         # "LinearRandom": bounds.LinearRandom(ref, table, attribs, steps=50),
    #         "LinearActive": bounds.LinearActive(ref, table, attribs, steps=50,
    #                                             epsilon=0.005,
    #                                             n_steps_converge=5)  # TODO
    #     }

    #     # Create a non-linear oracle function
    #     r = 20  # radius
    #     center = [50, 50]

    #     def distance(a, center):
    #         a = np.array(a)
    #         center = np.array(center)

    #         d = np.sqrt(np.sum((a - center) ** 2, axis=-1))

    #         return d

    #     def lower_is_better(q):
    #         x = np.array(q)[:,0]
    #         y = np.array(q)[:,1]
    #         b = np.sum(center)
    #         y_max = -x + b

    #         return y <= y_max

    #     def nl_oracle(q):
    #         return ((np.array(distance(q, center)) <= r) or
    #                 (lower_is_better(q)))


    #     # for eliciter in eliciters:
    #     #     samp_name = eliciter
    #     #     print(f'You are using {samp_name} Eliciter\n')
    #     #     outputs = run_bounds_eliciter(eliciters[eliciter], table,
    #     #                                   nl_oracle, ref,
    #     #                                   n_samples=100)
    #     #     (sample_choices, est_w, scores) = outputs

    #     #     if n_iter == 0:
    #     #         eli_scores[samp_name] = []
    #     #     else:
    #     #         eli_scores[samp_name].append(scores)
    #     #     if n_iter == max_iter-1:
    #     #         eli_choices[samp_name] = sample_choices
    #     # n_iter += 1

    # Create a non-linear oracle function
    r = 20  # radius
    center = [50, 50]

    def distance(a, center):
        a = np.array(a)
        center = np.array(center)
        dist = np.sqrt(np.sum((a - center) ** 2, axis=-1))
        return dist

    def lower_is_better(q):
        # dist = distance(q,center)
        # max_dist = distance([0,0],center)
        # return dist <= max_dist

        q = np.array(q)
        if q.ndim == 1:
            x = q[0]
            y = q[1]
        else:
            # if q.ndim > 2:
            #     n = q.shape[0] * q.shape[1] 
            #     q.reshape(n,2)
            x = q[:,0]
            y = q[:,1]
        b = np.sum(center)
        y_max = -x + b

        return y <= y_max

    def nl_oracle(q):
        # return np.logical_or((np.array(distance(q, center)) <= r),
        #                       lower_is_better(q))
        return (np.array(distance(q, center)) <= r)

    # ----------- visualisation --------------
    # sampler = eliciters["LinearActive"]
    # choices = eli_choices["LinearActive"]

    # Display 2D plot for nl_oracle ------------
    choices = -100 * np.random.random_sample((1000, 2)) + 100  # TODO
    labels = nl_oracle(np.array(choices))

    # Create an instance of Logistic Regression Classifier and fit the data.
    X = choices
    Y = labels
    # model = LogisticRegression()
    # model.fit(X, Y)

    # Plot the decision boundary. For that, we will assign a color to each
    # point in the mesh [x_min, x_max]x[y_min, y_max].
    x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
    y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
    h = 0.01  # step size in the mesh
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    # Z = model.predict(np.c_[xx.ravel(), yy.ravel()])  
    # TODO: nl_oracle
    Z = nl_oracle(np.c_[xx.ravel(), yy.ravel()])

    # Z = model(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    print(Z.shape)
    plt.figure()
    # plt.pcolormesh(xx, yy, Z, cmap=plt.cm.Paired)
    plt.contourf(xx, yy, Z, cmap=plt.cm.Spectral)
    # plt.colorbar()

    # Plot also the training points
    plt.scatter(X[:, 0], X[:, 1], c=Y, edgecolors="k", cmap=plt.cm.Spectral)
    # plt.xlabel("x")
    # plt.ylabel("y")

    # plt.xlim(xx.min(), xx.max())
    # plt.ylim(yy.min(), yy.max())
    # plt.xticks(())
    # plt.yticks(())

    plt.show()





    accept = []
    reject = []

    for i in range(len(labels)):
        if labels[i]:
            accept.append(choices[i])
        else:
            reject.append(choices[i])

    # print(len(accept), len(reject))

    # accept
    x = np.array(accept)[:, 0]
    y = np.array(accept)[:, 1]

    # reject
    a = np.array(reject)[:, 0]
    b = np.array(reject)[:, 1]

    # plt.figure()

    # plt.scatter(x, y, color='g',
    #             marker='o', label="accept")
    # plt.scatter(a, b, color='r',
    #             marker='x', label="reject")
    # plt.xlabel(attribs[0])
    # plt.ylabel(attribs[1])

    # TODO draw boundary (make a grid, evaluate oracle on grid, radius)
    # plot truth (circle)

    # u = np.arange(0, 100, 1)
    # v = np.arange(0, 100, 2)
    # U, V = np.meshgrid(u, v)

    # # print(U.shape, V.shape)
    # points = []

    # for j in range(len(v)):
    #     row = []
    #     for i in range(len(u)):
    #         row.append([u[i], v[j]])
    #     points.append(row)

    # labels = nl_oracle(np.array(points))
    # Z = np.array(labels)

    # plt.contour(U, V, Z, cmap=plt.cm.Spectral)
    # plt.scatter(U, V, c=Z)

    # # DEPEND ON CHOICES
    # x = np.array(choices)[:, 0]
    # y = np.array(choices)[:, 1]

    # Z = [labels] * len(y)
    # print(x, y, Z)
    # plt.contour(x,y, Z, cmap=plt.cm.Spectral)
    # plt.colorbar()
    # plt.scatter(x,y, c=Z)

    # TODO plot estimate boundary (query hasnt asked points) (line? <- logreg)

    # plt.legend()
    # plt.show()


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

        # TODO: only asking "Would you accept system_X?"

        # Display the choice between this and the reference
        # interface.text(elicit.Pair(sampler.query, ref))

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
    # print("Truth:    ", w_true)
    # print("Estimate: ", sampler.w)
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
