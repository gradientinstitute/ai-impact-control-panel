# Trying to infer a minimum viable set by refining a decision hyper-plane
# directly - perhaps with finite resolution
# import numpy as np
# from autograd import numpy as np, grad, hessian
import numpy as np
import matplotlib.pyplot as plt
# from scipy.optimize import minimize
from mpl_toolkits import mplot3d  # NOQA
from tqdm import tqdm
Poly = mplot3d.art3d.Poly3DCollection


# Research ideas
# 1. weight ambiguity (when weights are correlated?) is probably not an issue with synthetic values
# 2. axis-aligned questions


def main():

    # now do some quantatative analysis...
    dims = 3
    steps = 50
    reps = 500
    n_models = 2
    np.random.seed(42)

    scores = np.zeros((n_models, reps, steps))

    for rep in tqdm(range(reps)):
        ref = np.ones(dims)
        w_true = 0.1 + 0.9 * np.random.rand(dims)  # positive

        def truth(q):
            return ((q - ref)@w_true > 0).astype(float)

        models = [
            Simple(ref, 1.),
            Eigen(ref, 1.),
        ]

        for ix, sampler in enumerate(models):

            for st in range(steps):
                label = truth(sampler.choice)
                sampler.observe(label)

                # now mark it
                scores[ix, rep, st] = nrmse(w_true, sampler.w)

    if dims == 3:
        # compute intercept
        sampler = models[1]  # decide which model to display
        w = sampler.w
        intercept = np.diag(ref @ w / w)
        ax = plt.axes(projection='3d')
        ax.plot3D(*ref, 'go')
        intercept = np.diag(ref@w_true / w_true)
        ax.add_collection3d(Poly([intercept], alpha=0.25))
        ax.plot3D(*intercept, 'go', alpha=0)
        ax.add_collection3d(Poly([intercept], alpha=0.25, color="r"))
        ax.plot3D(*np.array(sampler.X).T, 'ko-', alpha=0.5)
        # ax.plot3D(*intercept, 'ko', alpha=0)
        set_axes_equal(ax)
        plt.show()

    # Asymptote is 1/x

    plt.figure()
    for ix, name, col in [(0, "Random ⊥ Weight", "r"),
                          (1, "Eigen ⊥ Weight", "b")]:
        lix = np.log(1+np.arange(steps))

        plt.plot(lix, np.log(scores[ix].mean(axis=0)), col)
        plt.fill_between(
            lix,
            *np.log(np.percentile(scores[ix], [10, 90], axis=0)),
            alpha=0.5,
            color=col,
            label=name,
        )
    plt.legend()
    plt.xlabel("Query number")
    plt.ylabel("Weight vector misalignment (unit vector RMSE)")
    plt.show()


def nrmse(w1, w2):
    """Normalise two weight vectors, then get RMSE."""
    d1 = w1 / (w1@w1)**.5
    d2 = w2 / (w2@w2)**.5
    return ((d1-d2)**2).sum() **.5


class Sampler:

    def __init__(self, ref, radius):
        self.ref = ref
        self.radius = radius

        # Initialise
        dims = len(ref)
        X = [ref+radius]
        for d in range(dims):
            v = ref + 0
            v[d] += radius
            X.append(v)
        self.X = X
        self._update()

    def observe(self, label):
        if label:
            self.X.append(self.choice)
        else:
            # if ref+a is a no, ref-a is a yes
            self.X.append(2*self.ref-self.choice)
        self._update()


class Eigen(Sampler):
    def _update(self):
        # Compute the weights
        diff = np.array(self.X) - self.ref[None, :]

        # linear discriminant analysis gives decision plane normal
        dcov = np.cov(diff.T)
        dmean = diff.mean(axis=0)
        w = np.linalg.solve(dcov, dmean)
        w /= (w@w)**.5  # normalise
        self.w = w

        # inject w as the largest eigenvalue
        K = dcov
        K = K + dcov.trace() * np.outer(w, w)
        eigv, eigm = np.linalg.eigh(K)

        # Explore along eigenvector with smallest eigenvalue
        dirn = self.radius * eigm[:, np.argmin(eigv)]
        self.choice = self.ref + dirn


class Simple(Sampler):

    def _update(self):
        # Compute the weights
        diff = np.array(self.X) - self.ref[None, :]

        # linear discriminant analysis gives decision plane normal
        dcov = np.cov(diff.T)
        dmean = diff.mean(axis=0)
        w = np.linalg.solve(dcov, dmean)
        w /= (w@w)**.5  # normalise
        self.w = w

        # Baseline heuristic - sample perpendicular to weight
        dims = len(self.ref)
        dirn = np.random.randn(dims)
        dirn -= w * (dirn @ w) / (w @ w)
        dirn *= self.radius / (dirn@dirn)**.5
        self.choice = self.ref + dirn


def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])


if __name__ == "__main__":
    main()
