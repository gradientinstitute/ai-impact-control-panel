import numpy as np

from deva.elicit import Candidate, Toy, VotingEliciter, ActiveRanking, \
                         ActiveMaxPrimary, ActiveMaxSmooth, ActiveMax


def input_gen(num=1000):
    '''Generate n random systems on the Pareto front'''
    # input number of systems generate
    systems = []
    while num > 0:
        angles = np.random.uniform(0, 1.5707963, 5)
        x1 = np.cos(angles[0])
        x2 = np.sin(angles[0])*np.cos(angles[1])
        x3 = np.sin(angles[0])*np.sin(angles[1])*np.cos(angles[2])
        x4 = np.sin(angles[0])*np.sin(angles[1])*np.sin(angles[2])\
            * np.cos(angles[3])
        x5 = np.sin(angles[0])*np.sin(angles[1])*np.sin(angles[2])\
            * np.sin(angles[3])*np.cos(angles[4])
        system = [x1, x2, x3, x4, x5]
        systems.append(np.array(system))
        num -= 1
    return systems


def favorate_gen(num=1000):
    '''Generate the favorate system at random,
    then sort the systems according to their distance to the favorate one'''
    favorate_index = np.random.randint(0, num, 1)[0]
    systems = input_gen(num)
    favorate_coor = systems[favorate_index]
    systems.sort(key=lambda system: np.linalg.norm(system
                 - favorate_coor))  # sort by the distance
    return systems


def test_eliciters(eliciter_list):
    '''Feed the generated system to eliciters,
    store the number of questions used to find the answer,
    as well as the distance between the answer found and the ground truth.'''
    candidates = []
    systems = favorate_gen(50)
    attributes = ["x1", "x2", "x3", "x4", "x5"]
    scenario = {}
    scenario['primary_metric'] = "x1"
    scenario['metrics'] = {}
    # make every attributes higher the better
    for attr in attributes:
        scenario['metrics'][attr] = {}
        scenario['metrics'][attr]['higherIsBetter'] = True
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
    return res


# sample usage
print(test_eliciters([Toy, VotingEliciter, ActiveRanking, ActiveMaxSmooth,
                     ActiveMaxPrimary, ActiveMax]))
