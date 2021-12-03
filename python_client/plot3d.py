import matplotlib.pyplot as plt
import matplotlib.patches as mpatches  # NOQA
from mpl_toolkits import mplot3d
import numpy as np

Poly3D = mplot3d.art3d.Poly3DCollection


def radius(choices):
    c = np.array(choices)[:, :3]
    # rad = radius  # don't need to clip tight
    return 0.8 * (c.max(axis=0) - c.min(axis=0))


def sample_trajectory(choices, attribs):
    # plot the sampler trajectory
    ax = plt.axes(projection='3d')
    c = np.array(choices)[:, :3]


    ax.plot3D(*c.T[:3], 'k-', alpha=0.5, label="Query Trajectory")
    ax.plot3D(*c.T[:3], 'ko', alpha=0.5, label="Query Systems")


    def m(name):
        ren = {
            "fp": "false positives",
            "fn": "false negatives",
            "profit": "net revenue"
        }
        return ren.get(name, name)

    ax.set_xlabel(m(attribs[0]))
    ax.set_ylabel(m(attribs[1]))
    ax.set_zlabel(m(attribs[2]))

    def ranger(v):
        a = v.min()
        b = v.max()
        return [1.2*a-.2*b, 1.2*b-.2*a]

    ax.set_xlim3d(*ranger(c[:, 0]))
    ax.set_ylim3d(*ranger(c[:, 1]))
    ax.set_zlim3d(*ranger(c[:, 2]))


def weight_disc(w, ref, radius, c, label="Boundary"):
    # If we truncated the weight vector it might not be a unit vector in 
    # this space
    w = w / (w@w)**.5

    v = w * radius
    v /= (v@v)**.5
    _, R = np.linalg.eigh(np.outer(v, v))
    theta = np.linspace(0, 2*np.pi, 101)
    diff = np.array((np.cos(theta), np.sin(theta), 0*theta)).T @ R.T
    diff = diff * radius
    ax = plt.gca()
    pts = ref + diff
    pts = pts[(pts > 0).all(axis=1)]
    ax.plot3D(*pts.T, alpha=0)
    collection = Poly3D([pts], color=c, alpha=0.5, label=label)

    # workaround for legend bug in matplotlib3d
    collection._facecolors2d = collection._facecolor3d
    collection._edgecolors2d = collection._edgecolor3d

    ax.plot3D(
        *ref[:3], 'o', markerfacecolor='#fff',
        markeredgecolor='#000', zorder=100, label="Reference system"
    )
    ax.add_collection3d(collection)

