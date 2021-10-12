import numpy as np


def main():
    # Some basic problem I have good intuitions for
    # context = dict(
    #     feats = ["acceleration", "fuel consumption", "price"],
    #     worse = ["slower", "worse", "higher"],
    #     better = ["faster", "better", "lower"],
    #     units = ["seconds", "litres", "x$1000"],
    #     direction = [-1, -1, 1],
    # )
    # ref = np.array([8, 7, 25])

    # And a fairness one I don't
    context = dict(
        feats=["error concentration", "gender inequality", "net profit"],
        worse=["increased", "increased", "less"],
        better=["reduced", "reduced", "more"],
        units=["individual errors", "error difference", "x $1000"],
        direction=[-1, -1, 1],  # direction of improvement
    )
    ref = np.array([8, 20, 250])  # Previous system

    # known hard bounds

    # TODO: try a reference system where one aspect can't be improved (eg its zero)
    # ref = np.array([8, 0, 50])  # inaction is likely to have some metrics "perfect" and some "terrible"
                                # this may require imputation


    # TODO: try a reference system where one aspect cant be worse

    # Conduct an AHP about the reference system
    dims = len(ref)
    A = np.ones((dims, dims))  # store estimates of "exchange rates"
    dirn = context["direction"]


    for rewarddim in range(dims):
        # if a value can't be reduced (will hit zero?)
        # then we shouldn't ask about trade-offs that involve sacrificing it
        # but can perhaps impute the slope by flipping the dimension

        # Offer a reward
        qry = ref + 0
        # improvement heuristic
        refv = ref[rewarddim]
        delta = min(refv, max(1, 10**np.floor(np.log10(refv) - 1)))
        reward = delta * dirn[rewarddim]  # or relative to reference
        qry[rewarddim] += reward
        # Ask for the price in each dimension
        for pricedim in range(dims):
            if rewarddim == pricedim:
                continue
            price = ask(qry, ref, pricedim, context)
            cost = price - ref[pricedim]
            # cost might be zero, reward is nonzero - store the cost/reward ratio
            A[rewarddim, pricedim] = cost/reward

    # Impute
    # TODO: how do we infer an exchange rate between dimensions when neither
    # can be reduced?

    # Assess with an AHP
    eigv, eigm = np.linalg.eig(A)
    ind = eigv.argmax()
    eigv[ind] # should be close to d
    print(f"Preference consistency: {1-abs(1 - eigv[ind]/dims):.0%}")
    w = eigm[:, ind]  # gives a weight vector
    w /= np.abs(w).max()

    # Get some random models and say whether they would be rejected or not...
    for i in range(10):
        qry = np.round(ref * (1 + 0.1 * np.random.randn(dims)), 1)
        delta = (qry-ref) @ w
        show(qry, ref, context)
        if delta > 0:
            print(f"Verdict: accept")
        else:
            print(f"Verdict: reject")
        print("\n\n")



def show(qry, ref, context):
    # same deal
    ask(qry, ref, -1, context)


def ask(qry, ref, asking, context):
    eps = 1e-5
    feats = context["feats"]
    worse = context["worse"]
    better = context["better"]
    units = context["units"]
    direction = context["direction"]

    if asking >= 0:
        print(f"Enter your maximum {feats[asking]} for this system to be better than the reference:")

    improved = ""
    for i, (q, r) in enumerate(zip(qry, ref)):
        if i == asking:
            continue
        feat = feats[i]
        if abs(q-r) > eps:
            # Changed
            is_better = (q - r) * direction[i] > 0
            if is_better:
                improved = feat
            sac = better[i] if is_better else worse[i]
            change = f"{r} → {q}"
            sacrifice = f"{sac} {feat}"
        else:
            sacrifice = f"same {feat}"
            change = q
        sacrifice += f" ({units[i]})"
        print(f"{sacrifice:>50s} {change}")

    if asking < 0:
        print("\n\n")
        return

    improve = direction[asking]
    # dirn = "at most" if improve < 0 else "at least"
    question = f"{feats[asking]} ({units[asking]})"
    change = f"{str(ref[asking])} → "
    prompt = f"{question:>50s} {change}"

    v = ref[asking] + improve

    while True:
        inp = input(prompt)
        try:
            v = float(inp)
        except:
            continue
        if (improve * (v - ref[asking]) <= 0):
            break
        print(f"    {improved} has improved. The {feats[asking]} cutoff shouldn't also need to be {better[asking]} to accept this system.")
    print("\n\n")
    return v


if __name__ == "__main__":
    main()
