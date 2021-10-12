"""Productionising LDA.py"""
from deva import fileio
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d  # NOQA
from deva import interface, elicit, bounds
Poly = mplot3d.art3d.Poly3DCollection


def main():
    np.random.seed(43)

    # Research ideas:
    # TODO: ask about 2 axes at a time only
    # TODO: what do we communicate at the end?
    # TODO: auto answer if query dominates or dominated...
    # TODO: ask about the real candidates first, then refine the model?
    # TODO: smart termination condition

    # Load a real scenario
    scenario_name = "fraud"  # "simple_fraud"
    candidates, meta = fileio.load_scenario(
        scenario_name, False, pfilter=False)
    cnames = [c.spec_name for c in candidates]
    reference = meta["reference_model"]
    metrics = meta["metrics"]
    assert reference in cnames

    # Estimate a suitable perturbation range
    attribs = list(candidates[0].attributes)  # establish a canonical order
    attribs = ['fp', 'fn', 'profit']  # restrict

    # Tabulate observed range
    # TODO: code might need some tweaking for ordinal data
    table = np.zeros((len(candidates), len(attribs)))
    for i, c in enumerate(candidates):
        table[i, :] = [c[a] for a in attribs]
    ref_ix = cnames.index(reference)
    ref = table[ref_ix]
    ref_candidate = candidates[ref_ix]
    ref_candidate.attributes = {a: ref_candidate[a] for a in attribs}
    ref_candidate.name = "Baseline"
    # ref_candidate.spec_name

    # heuristic for sample scale (some notion of importance of each dimension)
    # eg perturbation of 1 on accuracy is huge, on FP is nothing...
    radius = 0.5 * table.std(axis=0)

    # Also we need to know which direction is better?
    # -1 if lower is better, +1 if higher is better
    dims = len(ref)
    sign = np.ones(dims)
    for i, a in enumerate(attribs):
        if not metrics[a]["higherIsBetter"]:
            sign[i] = -1

    # now do some quantatative analysis... (simulate steps)
    steps = 50  # how many samples

    # Invent a hidden ground truth
    w_true = 0.1 + 0.9 * np.random.rand(dims)  # positive
    w_true *= sign / radius
    w_true /= (w_true @ w_true)**.5  # unit vector

    def oracle(q):
        return ((q - ref)@w_true > 0)

    # run a sampler - needs to know that lower is better?
    # If we use a different scale for each dimension,
    # perhaps we can hide the complexity
    sampler = Sampler(ref, radius * sign, steps)
    choices = []

    while not sampler.finished:
        # Create a synthetic candidate
        synth_candidate = elicit.Candidate(
            "Proposed",
            dict(zip(attribs, sampler.choice)),
            "null",
        )

        # set up a choice betweeen
        fchoice = elicit.Pair(
            synth_candidate,  # comparisons towards this
            ref_candidate,
        )
        interface.text(fchoice, metrics)

        # print(sampler.choice)
        choices.append(sampler.choice)
        label = oracle(sampler.choice)
        if label:
            print("Choice: (ACCEPT) proposed.\n\n")
        else:
            print("Choice: (REJECT) proposed.\n\n")
        sampler.observe(label)

    # compute intercept
    w = sampler.w
    w = w / (w@w)**.5

    # Compare sampler scores to true scores:
    print("Experimental results")
    print("--------------------------")
    print("Truth:", w_true)
    print("Estimate:", w)

    # Sanity check
    accept = oracle(table)
    print(f"Truth would accept {np.mean(accept):.0%} of candidates.")

    def guess(q):
        return ((q - ref)@w >= 0)
    pred = guess(table)
    print(f"Candidates labeled with {np.mean(accept==pred):.0%} accuracy.")
    print("See sampling plot")

    # Result plotting code ---------------------------------

    # plot the sampler trajectory
    ax = plt.axes(projection='3d')

    # Get an in-plane rotation matrix
    c = np.array(choices)[:, :3]
    # rad = radius  # don't need to clip tight
    rad = c.max(axis=0) - c.min(axis=0)

    plot_weight_disc(w[:3], ref[:3], .8*rad[:3], 'r')
    plot_weight_disc(w_true[:3], ref[:3], .8*rad[:3], 'b')

    # draw the planes as a dish?
    ax.plot3D(*c.T[:3], 'ko-', alpha=0.5)
    ax.plot3D(*ref[:3], 'go')
    ax.set_xlabel(attribs[0])
    ax.set_ylabel(attribs[1])
    ax.set_zlabel(attribs[2])

    def ranger(v):
        a = v.min()
        b = v.max()
        return [1.2*a-.2*b, 1.2*b-.2*a]

    ax.set_xlim3d(*ranger(c[:, 0]))
    ax.set_ylim3d(*ranger(c[:, 1]))
    ax.set_zlim3d(*ranger(c[:, 2]))
    plt.show()



def plot_weight_disc(w, ref, radius, c):
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
    ax.add_collection3d(Poly([pts], color=c, alpha=0.5))


class Sampler:

    def __init__(self, ref, radius, steps):
        ref = np.asarray(ref)
        radius = np.asarray(radius)
        self.ref = ref
        self.radius = radius
        dims = len(ref)
        self.step = 0
        self.steps = steps

        # Initialise
        X = [ref+radius]
        for d in range(dims):
            v = ref + 0
            # these labels are virtual / allowed to go negative
            v[d] += radius[d]  # adding radius makes it better
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

    def _update(self):
        # linear discriminant analysis gives a decision plane normal
        self.step += 1
        diff = np.array(self.X) - self.ref[None, :]
        dcov = np.cov(diff.T)
        dmean = diff.mean(axis=0)
        w = np.linalg.solve(dcov, dmean)
        w /= (w@w)**.5  # normalise
        self.w = w

        dims = len(self.ref)
        choice = np.zeros(dims) - 1
        while (choice < 0).any():
            # Question: should sampling density be affected by scale?
            # I'd say yes given we're showing aperson
            # diff = np.random.randn(len(self.ref)) # uniform
            diff = np.random.randn(len(self.ref)) * self.radius
            diff -= w * (diff @ w) / (w @ w)  # make perpendicular
            diff /= np.sum((diff/self.radius)**2) ** .5  # re-normalise
            choice = self.ref + diff
        self.choice = choice
        return

    @property
    def finished(self):
        return self.step > self.steps


if __name__ == "__main__":
    main()
