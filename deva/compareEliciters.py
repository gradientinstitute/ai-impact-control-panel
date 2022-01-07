import numpy as np

from deva.elicit import Candidate, Toy, VotingEliciter, ActiveRanking, \
                         ActiveMaxPrimary, ActiveMaxSmooth, ActiveMax


def input_gen(num=1000, attr=5):
    '''Generate n random systems on the Pareto front'''
    # input number of systems generate
    # ref: https://en.wikipedia.org/wiki/N-sphere#Spherical_coordinates
    systems = []
    while num > 0:
        system = []
        acc = 1
        angles = np.random.uniform(0, 1.5707963, attr)
        for x in range(attr):
            system.append(acc*np.cos(angles[x]))
            acc *= np.sin(angles[x])
        systems.append(np.array(system))
        num -= 1
    return systems


def favourite_gen(num=1000, attr=5):
    '''Generate the favourite system at random,
    then sort the systems according to their distance to the favourite one'''
    favourite_index = np.random.randint(0, num, 1)[0]
    systems = input_gen(num, attr)
    favourite_coor = systems[favourite_index]
    systems.sort(key=lambda system: np.linalg.norm(system
                 - favourite_coor))  # sort by the distance
    return systems


def test_eliciters(eliciter_list, num, attr):
    '''Feed the generated system to eliciters,
    store the number of questions used to find the answer,
    as well as the distance between the answer found and the ground truth.'''
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
    for eliciter in eliciter_list:
        question_count = 0
        test_target = eliciter(candidates, scenario)
        while not test_target.terminated:
            question_count += 1
            m1, m2 = test_target.query
            if int(m1.name) < int(m2.name):
                # choose the better option, smaller the better
                test_target.input(m1)
            else:
                test_target.input(m2)
        result = test_target.result
        error = {}
        error['distance'] = np.linalg.norm(systems[0] - systems[result.name])
        error['question_count'] = question_count
        res[str(eliciter)] = error
    return [num, attr, res]


def print_result(result):
    '''Print the result with explainations'''
    num, attr, res = result
    print_str = f'The eliciters are tested using {num} systems,' \
        f' each of the systems has {attr} attributes. \n'
    for key in res.keys():
        name = key.split('.')[-1].split("'")[0]
        question_count = res[key]['question_count']
        distance = res[key]['distance']
        print_str += f'\nEliciter: {name}\nNum Questions: {question_count}\n'\
            f'Error: {distance}\n'
    print(print_str)


if __name__ == "__main__":
    # sample usage
    print_result(test_eliciters([Toy, VotingEliciter, ActiveRanking,
                                ActiveMaxSmooth,
                                ActiveMaxPrimary, ActiveMax], 50, 3))
