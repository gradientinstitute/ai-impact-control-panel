from deva import elicit
import numpy as np
from deva.pareto import remove_non_pareto
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from collections import OrderedDict


def system_gen_lower(num=1000, attr=5):
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


systems = system_gen_lower(100, 2)

candidates = []
attributes = []
for x in range(2):
    n = x + 1
    attributes.append(f"x{n}")
scenario = {}
scenario["primary_metric"] = "x1"
scenario["metrics"] = {}

sys_dict = {}
for index, system in enumerate(systems):
    sys_dict[str(index)] = dict(zip(attributes, system))

systems = remove_non_pareto(sys_dict)

res = {}  # key: eliciter, value: error
for name in systems.keys():
    candidates.append(elicit.Candidate(name, systems[name]))

# init eliciter
nadir_list = []
ideal_list = []
current_centers_list = []
candidates_list = [candidates]
kmeans_centers_list = []
test_target = elicit.Enautilus(candidates, scenario)
while not test_target.terminated():
    m1, m2 = test_target.query()
    nadir, ideal, attribs, current_centers, candidates, kmeans_centers =\
        test_target.plot_data()
    nadir_list.append(nadir)
    ideal_list.append(ideal)
    current_centers_list.append(current_centers)
    kmeans_centers_list.append(kmeans_centers)
    test_target.plot_2d()
    test_target.put(m1.name)
test_target._update()
nadir, ideal, attribs, current_centers, candidates, kmeans_centers =\
    test_target.plot_data()
nadir_list.append(nadir)
ideal_list.append(ideal)
current_centers_list.append(current_centers)
kmeans_centers_list.append(kmeans_centers)
plt.figure()
for can in candidates_list[0]:
    point1 = np.array(can.get_attr_values())
    plt.scatter(point1[0], point1[1], c='gray', alpha=0.4,
                label='Candidates')
for index, nadir in enumerate(nadir_list):
    width = nadir[attribs[0]] - ideal_list[index][attribs[0]]
    height = nadir[attribs[1]] - ideal_list[index][attribs[1]]
    currentAxis = plt.gca()
    currentAxis.add_patch(Rectangle((ideal_list[index][attribs[0]],
                          ideal_list[index][attribs[1]]),
                          width, height, fill=None, alpha=0.1))
    plt.scatter(ideal_list[index][attribs[0]], ideal_list[index][attribs[1]],
                s=80, marker=(5, 1), c='gray')
    plt.scatter(nadir[attribs[0]], nadir[attribs[1]],
                s=80, marker=(3, 1), c='gray')
    for point2 in kmeans_centers_list[index]:
        plt.scatter(point2[0], point2[1], c='gray', alpha=0.2
                    )
        p1 = [point2[0], nadir[attribs[0]]]
        p2 = [point2[1],
              nadir[attribs[1]]]
        plt.plot(p1, p2, c='gray',
                 linestyle='dotted', alpha=0.2)
for ccl in current_centers_list:
    for point in ccl:
        plt.scatter(point[0], point[1], c='gray', alpha=0.2
                    )
width = nadir[attribs[0]] - ideal_list[-1][attribs[0]]
height = nadir[attribs[1]] - ideal_list[-1][attribs[1]]
currentAxis = plt.gca()
currentAxis.add_patch(Rectangle((ideal_list[-1][attribs[0]],
                                ideal_list[-1][attribs[1]]),
                                width, height, fill=None, alpha=0.1))
plt.scatter(ideal_list[-1][attribs[0]], ideal_list[-1][attribs[1]],
            s=80, marker=(5, 1), label='Trade-off Margins', c='purple')
plt.scatter(nadir[attribs[0]], nadir[attribs[1]],
            s=80, marker=(3, 1), label='Nadir Point', c='blue')
for point in current_centers:
    plt.scatter(point[0], point[1], c='orange', alpha=0.2,
                label='Virtual Options')
for can in candidates:
    point1 = np.array(can.get_attr_values())
    plt.scatter(point1[0], point1[1], c='red', alpha=0.3,
                label='Candidates')
for point2 in kmeans_centers:
    plt.scatter(point2[0], point2[1], c='green', alpha=0.2,
                label='KMeans Centers')
    p1 = [point2[0], nadir[attribs[0]]]
    p2 = [point2[1],
          nadir[attribs[1]]]
    plt.plot(p1, p2, c='green',
             linestyle='dotted', alpha=0.2)
handles, labels = plt.gca().get_legend_handles_labels()
by_label = OrderedDict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())
plt.title('Overlapping view of all iterations')
plt.savefig('overlap.jpg')
test_target.plot_final()
result = test_target.result
