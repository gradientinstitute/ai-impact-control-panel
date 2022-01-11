import numpy as np
import matplotlib.pylab as plt
import click
from deva.elicit import Candidate, Toy, VotingEliciter, ActiveRanking, \
                         ActiveMaxPrimary, ActiveMaxSmooth, ActiveMax


def system_gen(num=1000, attr=5):
    '''Generate n random systems on the Pareto front
    by sampling from the surface of a hypersphere.
    num is the number of systems we would like to generate,
    attr is the number of dimensions each system has.'''
    # input number of systems generate
    # ref: https://en.wikipedia.org/wiki/N-sphere#Spherical_coordinates
    systems = []
    while num > 0:
        system = []
        acc = 1
        angles = np.random.uniform(0, np.pi/2, attr)
        for x in range(attr):
            system.append(acc*np.cos(angles[x]))
            acc *= np.sin(angles[x])
        systems.append(np.array(system))
        num -= 1
    return systems


def favourite_gen(num=1000, attr=5):
    '''Generate the favourite system at random,
    then sort the systems according to their distance to the favourite one.
    num is the number of systems we would like to generate,
    attr is the number of dimensions each system has'''
    favourite_index = np.random.randint(0, num, 1)[0]
    systems = system_gen(num, attr)
    favourite_coor = systems[favourite_index]
    systems.sort(key=lambda system: np.linalg.norm(system
                 - favourite_coor))  # sort by the distance
    return systems


def test_eliciters(eliciter_list, num, attr):
    '''Feed the generated system to eliciters,
    store the number of questions used to find the answer,
    as well as the distance between the answer found and the ground truth.
    num is the number of systems we would like to generate,
    attr is the number of dimensions each system has'''
    # transfer from string to function
    e_list = []
    eliciters_map = {"TOY": Toy, "ACTIVERANKING": ActiveRanking,
                     "ACTIVEMAX": ActiveMax,
                     "ACTIVEMAXSMOOTH": ActiveMaxSmooth,
                     "ACTIVEMAXPRIMARY": ActiveMaxPrimary,
                     "VOTINGELICITER": VotingEliciter}
    for e in eliciter_list:
        e = e.upper()
        e_list.append(eliciters_map[e])
    # start prep for testing
    candidates = []
    systems = favourite_gen(num, attr)
    attributes = []
    for x in range(attr):
        n = x+1
        attributes.append(f"x{n}")
    scenario = {}
    scenario['primary_metric'] = "x1"
    scenario['metrics'] = {}
    # make every attributes higher the better
    for a in attributes:
        scenario['metrics'][a] = {}
        scenario['metrics'][a]['higherIsBetter'] = True
    res = {}  # key: eliciter, value: error
    for index, system in enumerate(systems):
        candidates.append(Candidate(index, dict(zip(attributes, system))))
    # use the generated candidates to test eliciters
    for eliciter in e_list:
        question_count = 0
        error_record = []
        test_target = eliciter(candidates, scenario)
        while not test_target.terminated:
            question_count += 1
            # calculate the error between remaining candidate in the eliciter
            # and the ground truth
            candidate_list = []
            for c in test_target.candidates:
                candidate_list.append(np.array(list(c.get_attr())))
            error_record.append(np.linalg.norm(systems[0] -
                                np.mean(candidate_list)))
            m1, m2 = test_target.query
            if int(m1.name) < int(m2.name):
                # choose the better option, smaller the better
                test_target.input(m1)
            else:
                test_target.input(m2)
        result = test_target.result
        mean_error = np.mean(np.linalg.norm(systems[0] - systems))
        error = {}
        error['distance'] = np.linalg.norm(systems[0] - systems[result.name])
        error['question_count'] = question_count
        error_record.append(error['distance'])
        plt.plot(error_record, range(1, len(error_record)+1))
        plt.savefig('plot.jpg')
        res[str(eliciter)] = error
    return [num, attr, mean_error, res]


def print_result(result):
    '''Print the result with explainations'''
    num, attr, mean_error, res = result
    print_str = f'The eliciters are tested using {num} systems,' \
        f' each of the systems has {attr} attributes. \n'\
        'The errors were calculated by the Euclidean distance between the'\
        ' result and the ground truth, the expected error of a random'\
        f' guess would be {mean_error:.3}.\n'
    for key in res.keys():
        name = key.split('.')[-1].split("'")[0]
        question_count = res[key]['question_count']
        distance = res[key]['distance']
        print_str += f'\nEliciter: {name}\nNum Questions: {question_count}\n'\
            f'Error: {distance:.3}\n'
    print(print_str)


@click.command()
@click.option('-e', '--eliciters', default=["Toy", "VotingEliciter",
                                            "ActiveRanking",
                                            "ActiveMaxSmooth",
                                            "ActiveMaxPrimary", "ActiveMax"],
              multiple=True,
              help='the eliciters you want to compare in a list,\
                 choose two or more from ')
@click.option('-n', '--number', default=50,
              help='the number of cadidate to be generated')
@click.option('-d', '--dimension', default=3,
              help='dimensions each candidate has.')
def compareEliciters(eliciters, number, dimension):
    print_result(test_eliciters(eliciters, number, dimension))


if __name__ == "__main__":
    compareEliciters()
    # # sample usage
    # print_result(test_eliciters([Toy, VotingEliciter, ActiveRanking,
    #                             ActiveMaxSmooth,
    #                             ActiveMaxPrimary, ActiveMax], 50, 3))
