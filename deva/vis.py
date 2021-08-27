"""
Very simple mock-up of a comparison vis.
Can hook into the framework afterwards.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from os import path
import numpy as np


def nice_number(x, sigfig=2):
    # Write a potentially large number in limited detail
    x = int(x)
    n = len(str(x))
    x = round(x, -n+3)
    if x > 1e6:
        s = f"{x/1e6:.1f}M"
    elif x > 1e3:
        s = f"{x/1e3:.1f}K"
    else:
        s = str(x)
    s = s.replace(".0", "")
    return s


def get_context(sys1, sys2, scale, a, high_is_good):

    context = {
        "A": sys1["name"],
        "a": sys1["name"].split()[-1],
        "X": nice_number(sys1[a]),
    }

    perf = sys1[a] / scale[a]
    if not high_is_good:
        perf = 1 - perf
    if perf > 0.99:
        context["rel"] = "best"
    elif perf > 0.75:
        context["rel"] = "relatively good"
    elif perf < 0.01:
        context["rel"] = "worst"
    elif perf < 0.25:
        context["rel"] = "relatively poor"
    else:
        context["rel"] = "average"
    # print(perf, context["rel"])
    if sys2:
        v1 = sys1[a]
        v2 = sys2[a]
        diff = np.abs(v1-v2)
        if np.isclose(diff, 0):
            context["X"] = ""
        else:
            context["X"] = nice_number(diff)
        context["B"] = sys2["name"]
        context["b"] = sys2["name"].split()[-1]

        # prime the potential context words
        for word in ["less", "more", "fewer", "additional", "higher", "lower",
                     "same", "equal"]:
            context[word] = ""

        if v1 > v2:
            context["more"] = "more"
            context["additional"] = "additional"
            context["higher"] = context["A"]
            context["lower"] = context["B"]
        elif v2 > v1:
            context["less"] = "less"
            context["fewer"] = "fewer"
            context["higher"] = context["B"]
            context["lower"] = context["A"]
        else:
            context["same"] = "the same number of"
            context["equal"] = "equal"

    return context


icons = None


def load_icons(icon_file, pad=0):
    # print("load icons")
    # find icons regardless of directory
    icon_file = path.join(path.dirname(path.abspath(__file__)), "icons2.png")
    icon_key = ["profit", "FNWO", "FPWO", "FP", "FN", "CORRECT", "INCORRECT"]
    raw = (plt.imread(icon_file) * 255).astype(np.uint8)

    # raw = raw[:, 3:-3]
    icon_w = raw.shape[1]
    icon_h = raw.shape[0] // len(icon_key)

    icons = {}
    for i, name in enumerate(icon_key):
        y = i*icon_h
        icons[name] = raw[y:y+icon_h]

    if pad > 0:
        blank = 255 * np.ones((pad, icon_w, 4), np.uint8)
        blank[:, :, -1] = 0  # set transparent alpha
        for i in icons:
            icons[i] = np.vstack((
                icons[i],
                blank,
            ))
        return icons

    return icons


def comparison(sys1, sys2, scale=None, buttons=False, show_units=True,
               remap=None):
    global icons
    if not icons:
        icons = load_icons("icons2.png", 200)  # for top title
        # icons = load_icons("icons2.png", 50)

    unit = {
        "profit": "",  # special case"profit",
        "FN": "transactions",
        "FP": "transactions",
        "FNWO": "customers",
        "FPWO": "customers",
    }

    # long descriptions
    attribute = {
        "profit": "Net profit",
        "FN": "Undetected fraudulent transactions",
        "FP": "Incorrectly blocked transactions",
        "FNWO": "Recurrent undetected fraud",
        "FPWO": "Recurrent incorrect blocking",
    }

    # clobber the above if user specifies a specific naming scheme
    if remap:
        unmap = {k:v for v, k in remap.items()}
        attribute = {k:unmap[k] for k in unit}

    isgood = {
        "profit": True,
        "FN": False,
        "FP": False,
        "FNWO": False,
        "FPWO": False,
    }

    good_cols = ['darkgreen', 'springgreen']
    bad_cols = ['darkred', 'salmon']

    # Find the maximum value of any count unit
    if scale is None:
        assert sys2 is not None
        # autoscale
        scale = {}
        for sys in [sys1, sys2]:
            if sys is None:
                continue
            for n, v in sys.items():
                u = n  # unit[n]  # scale by unit accross all?
                if (u not in scale) or (v > scale[u]):
                    scale[u] = v

    # comparison = {
    #     "profit": "{higher} is better: it generates ${X} more profit.",
    #     "FN": ("{lower} is better: it prevents an additional {X}"
    #            " fraudulent transactions."),
    #     "FNWO": ("{lower} is better: {X} fewer customers experience"
    #              " repeated fraud."),
    #     "FP": ("{lower} is better: it "
    #            "approves an additional {X} legitimate transactions."),
    #     "FPWO": ("{lower} is better: {X} fewer customers are "
    #              "repeatedly blocked."),
    # }
    comparison = {
        "profit": "{A} generates ${X} {more}{less}{equal} profit.",
        "FN": "{A} misses {X} {more}{fewer}{same} fraudulent transactions.",
        "FNWO": ("{A} burdens {X} {additional}{fewer}{same} customers with"
                 " recurrent undetected fraud."),
        "FP": ("{A} blocks {X} {more}{fewer}{same} legitimate transactions."),
        "FPWO": ("{A} burdens {X} {additional}{fewer}{same} customers with "
                 "recurrent incorrect blocking."),
    }

    description = {
        "profit": "The system generates ${X} in profit ({rel}).",
        "FN": "{X} fraudulent transactions are overlooked ({rel}).",
        "FNWO": "{X} customers have frequent undetected frauds ({rel}).",
        "FP": "{X} legitimate transactions are blocked ({rel}).",
        "FPWO": "{X} customers have frequent blocked transactions ({rel}).",
    }

    ax = plt.gca()
    cols = ['red', 'blue']

    icon_h, icon_w = icons["FN"].shape[:2]

    barw = 6 * icon_w
    margin = icon_w * 1.05  # adjust margin here
    left = icon_w * 1.3  # adjust margin here
    right = left + barw

    y = 0
    tiles = []
    for a in unit:
        tile = icons[a]
        tiles.append(tile)
        fs = 12
        s = scale[a]  # scale[unit[a]]
        barh = .2
        pre = "$" if a == "profit" else ""
        context = get_context(sys1, sys2, scale, a, isgood[a])

        title_x = (margin + right)/2
        title_y = y # - 0.25 * icon_w
        plt.text(
            title_x, title_y, attribute[a], fontsize=12,
            va="center", ha="center", fontweight="bold")

        if sys2 is not None:
            text = comparison
            problem = zip([0, 1], [sys1, sys2], [.5-barh*1.25, .5 + barh*0.25])
        else:
            text = description
            problem = [[0, sys1, 0.5]]

        plt.text(0, y + 1.1*icon_w, text[a].format(**context), fontsize=fs)

        for colind, sys, offset in problem:

            if isgood[a]:
                cols = good_cols
            else:
                cols = bad_cols

            col = cols[colind]
            yy = y + offset * icon_w
            patchw = sys[a] * barw / s
            rx = left
            text_x = right + 0.125 * icon_w
            text_y = yy + 0.125*icon_w
            midy = yy + barh * icon_w/2
            plt.text(margin, text_y, sys["name"].split()[-1], fontsize=fs,
                     va="center", fontweight="bold")
            if isgood[a]:
                plt.plot([rx+1+patchw, right+1],  [midy, midy], ":",
                         color=bad_cols[colind], linewidth=3, alpha=0.5)
            else:
                rx = right - patchw  # flip
                plt.plot([left-1, rx-1],  [midy, midy], ":",
                         color=good_cols[colind], linewidth=3, alpha=0.5)

            patch = Rectangle((rx, yy), patchw, barh*icon_w, facecolor=col)
            ax.add_patch(patch)

            post = " " + unit[a] if show_units else ""
            plt.text(text_x, text_y, pre+nice_number(sys[a])+post,
                     va="center", fontsize=fs)  # , fontweight="bold")
        y += icon_h

    img = np.vstack(tiles)
    plt.imshow(img)
    plt.axis('off')
    plt.ylim([0, img.shape[0]])
    plt.xlim([0, icon_w * 10])

    if buttons:
        # draw the options to display
        pass

    ax.invert_yaxis()


def main():

    sys1 = {
        "name": "System A",
        "profit": 40128,
        "FN": 31,
        "FNWO": 6,
        "FP": 2103,
        "FPWO": 13,
    }

    sys2 = {
        "name": "System B",
        "profit": 20463,
        "FN": 43,
        "FNWO": 3,
        "FP": 3360,
        "FPWO": 6,
    }

    # maximum ever seen accross all models? some baseline
    maxv = {
        "profit": 50000,
        "FN": 100,
        "FNWO": 10,
        "FP": 4000,
        "FPWO": 13,
    }

    plt.figure(figsize=(10, 8))
    comparison(sys1, sys2)

    plt.figure(figsize=(10, 8))
    comparison(sys1, sys2, scale=maxv, buttons=True)

    plt.figure(figsize=(10, 8))
    comparison(sys1, None, scale=maxv)
    plt.show(block=False)
    input()  # test the block/console interaction


if __name__ == "__main__":
    main()
