"""Command line tool for experimentally comparing eliciters."""
import numpy as np
import matplotlib.pylab as plt
import click
from deva import elicit
from collections import namedtuple


def system_gen(num=1000, attr=5):
    """
    Generate n random systems on the Pareto front.

    The approach samples from the surface of a hypersphere.
    num is the number of systems we would like to generate,
    attr is the number of dimensions each system has.
    """
    # input number of systems generate
    # ref: https://en.wikipedia.org/wiki/N-sphere#Spherical_coordinates
    systems = []
    while num > 0:
        system = []
        acc = 1
        angles = np.random.uniform(np.pi, np.pi / 2, attr)
        for x in range(attr):
            system.append(acc * np.cos(angles[x]))
            acc *= np.sin(angles[x])
        systems.append(np.array(system))
        num -= 1
    systems = np.array(systems)
    for ind in range(attr):
        systems[:, ind] -= systems[:, ind].min()
    return systems


def cal_distance(candidate, goal):
    """calculate the distance between an option
    and the favorate candidate (goal)"""
    can = np.array(candidate.get_attr_values())
    g = np.array(goal.get_attr_values())
    return np.linalg.norm(can - g)


def test_eliciters(eliciter_list, num, attr):
    """
    Feed a generated system into eliciters.

    store the number of questions used to find the answer,
    as well as the distance between the answer found and the ground truth.
    num is the number of systems we would like to generate,
    attr is the number of dimensions each system has.
    """
    # transfer from string to function
    e_list = []
    for e in eliciter_list:
        if e == "Enautilus":
            # compare 3 enautilus when enautilus is added to the loop
            e_list.append(elicit.Enautilus)
            e_list.append(elicit.Enautilus)
        e_list.append(elicit.algorithms[e])
    # start prep for testing
    candidates = []
    systems = system_gen(num, attr)
    attributes = []
    for x in range(attr):
        n = x + 1
        attributes.append(f"x{n}")
    scenario = {}
    scenario["primary_metric"] = "x1"
    scenario["metrics"] = {}

    res = {}  # key: eliciter, value: error
    for index, system in enumerate(systems):
        candidates.append(elicit.Candidate(index,
                                           dict(zip(attributes, system))))
    favourite_index = np.random.randint(0, num, 1)[0]
    goal = candidates[favourite_index]
    enautilus_count = 1
    # use the generated candidates to test eliciters
    for eliciter in e_list:
        question_count = 0
        test_target = eliciter(candidates, scenario)
        name = str(eliciter)
        if test_target.description() == "E-NAUTILUS eliciter":
            enautilus_count *= 5
            test_target.updateForN(enautilus_count, 9)
            name = f".Enautilus {9} options {enautilus_count} Question limits'"
        while not test_target.terminated:
            question_count += 1
            options = test_target.query
            min_o = None
            put_name = None
            for o in options:
                dis = cal_distance(o, goal)
                if min_o is None or dis < min_o:
                    min_o = dis
                    put_name = o.name
            test_target.put(put_name)
        result = test_target.result
        mean_error = np.mean(np.linalg.norm(systems[favourite_index]
                                            - systems))
        error = {}
        error["distance"] = np.linalg.norm(systems[favourite_index]
                                           - systems[result.name])
        error["question_count"] = question_count
        res[name] = error
    return [num, attr, mean_error, res]


def print_result(result):
    """Print a result with explainations."""
    num, attr, mean_error, res = result
    print_str = f"The eliciters are tested using {num} systems," \
        f" each of the systems has {attr} attributes. \n"\
        "The errors were calculated by the Euclidean distance between the"\
        " result and the ground truth, the expected error of a random"\
        f" guess would be {mean_error:.3}.\n"
    for key in res.keys():
        name = key.split(".")[-1].split("'")[0]
        question_count = res[key]["question_count"]
        distance = res[key]["distance"]
        print_str += f"\nEliciter: {name}\nNum Questions: {question_count}\n"\
            f"Error: {distance:.3}\n"
    print(print_str)


@click.command()
@click.option("-e", "--eliciters", default=elicit.algorithms,
              multiple=True,
              help=f"The eliciters you want to compare,\
                    choose from {list(elicit.algorithms)}.\n\
                     Sample usage: -e Toy -e ActiveMax")
@click.option("-n", "--number", default=50,
              help="The number of cadidate to be generated")
@click.option("-d", "--dimension", default=3,
              help="Dimensions each candidate has.")
@click.option("-r", "--runs", default=10,
              help="The number of runs to average out outliers.")
def compareEliciters(eliciters, number, dimension, runs):
    Result = namedtuple("Result",
                        "numberCandidate numberAttributes meanError errorLog")
    result = Result(number, dimension, [], {})
    varLog = {}
    for _ in range(runs):
        num, attr, mean_error, res = test_eliciters(eliciters,
                                                    number, dimension)
        result.meanError.append(mean_error)
        for eliciter in res.keys():
            if eliciter not in varLog.keys():
                varLog[eliciter] = {"distance": [],
                                    "question_count": []}
            varLog[eliciter]["distance"].append(res[eliciter]["distance"])
            varLog[eliciter]["question_count"].append(
                res[eliciter]["question_count"])
    for eliciter in res.keys():
        result.errorLog[eliciter] = {"distance": 0,
                                     "question_count": 0}
        for key in result[3][eliciter]:
            result.errorLog[eliciter][key] = np.mean(varLog[eliciter][key])
    result = result._replace(meanError=np.mean(result.meanError))
    print_result(result)
    for eliciter in res.keys():
        plt.plot(result[3][eliciter]["question_count"],
                 result[3][eliciter]["distance"], marker="x",
                 label=eliciter)
    plt.plot(0, result[2], marker="x", label="Random guess eliciter")
    plt.title(f"Eliciter comparison. Number of cadidates={number},"
              f"number of attributes={dimension}")
    plt.xlabel("Number of questions")
    plt.ylabel("Error")
    plt.legend()
    plt.savefig("plot.jpg")
    # # box plot
    error = []
    question = []
    # scatter cloud
    plt.figure()
    for eliciter in res.keys():
        x = varLog[eliciter]["distance"]
        y = varLog[eliciter]["question_count"]
        error.append(x)
        question.append(y)
        plt.scatter(x, y, marker="o", alpha=0.2, label=eliciter)
    plt.scatter(result.meanError, 0, marker="o", label="Random guess eliciter")
    plt.title(f"{runs} runs that vary system attributes and user preferences"
              f"\nNumber of cadidates={number},"
              f"number of attributes={dimension}")
    plt.ylabel("Number of questions")
    plt.xlabel("Error")
    plt.legend()
    # plt.savefig("scatterCloud.jpg")
    # box plot for error
    plt.figure()
    plt.boxplot(error, 0, "")
    loc = range(1, len(eliciters) + 1)
    plt.xticks(loc, eliciters, fontsize=5.5)
    plt.ylabel("Error")
    plt.title("Box plot for errors")
    # plt.savefig("errorBoxplt.jpg")
    # box plot for # of questions
    plt.figure()
    plt.boxplot(question, 0, "")
    loc = range(1, len(eliciters) + 1)
    plt.xticks(loc, eliciters, fontsize=5.5)
    plt.ylabel("Number of questions")
    plt.title("Box plot for number of questions")
    # plt.savefig("q#Boxplt.jpg")
    plt.show()


if __name__ == "__main__":
    compareEliciters()
    # # sample usage
    # print_result(test_eliciters([Toy, VotingEliciter, ActiveRanking,
    #                             ActiveMaxSmooth,
    #                             ActiveMaxPrimary, ActiveMax], 50, 3))
