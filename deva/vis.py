"""
Very simple mock-up of a comparison vis.
Can hook into the framework afterwards.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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


def load_icons(icon_file, pad=0):
    icon_file = "icons2.png"
    icon_key = ["profit", "FNWO", "FPWO", "FP", "FN", "CORRECT", "INCORRECT"]
    raw = (plt.imread(icon_file) * 255).astype(np.uint8)
    raw = raw[:, 3:-3]
    icon_res = raw.shape[1]
    icons = {}
    for i, name in enumerate(icon_key):
        y = i*icon_res
        icons[name] = raw[y:y+icon_res]

    if pad > 0:
        blank = 255 * np.ones((pad, icon_res, 4), np.uint8)
        blank[:, :, -1] = 0  # set transparent alpha
        for i in icons:
            icons[i] = np.vstack((
                icons[i],
                blank,
            ))
        return icons


    return icons

icons = load_icons("icons2.png", 50)

def comparison(sys1, sys2):

    unit = {
        "profit": "profit",
        "FN": "FNT",
        "FP": "FPT",
        "FNWO": "person",
        "FPWO": "person",
    }

    # Find the maximum value of any count unit
    scales = {}
    for sys in [sys1, sys2]:
        for n, v in sys.items():
            u = unit[n]
            if (u not in scales) or (v > scales[u]):
                scales[u] = v

    description = {
        "profit": "net system profit",
        "FN": "total undetected fraudulent transactions",
        "FNWO": "customers with excessive undetected fraud",
        "FP": "total incorrectly blocked transactions",
        "FPWO": "customers with excessive blocked legitimate transactions",
    }

    ax = plt.gca()
    cols = ['purple', 'blue']

    icon_h, icon_w = icons["FN"].shape[:2]

    barw = 6 * icon_w 
    y = 0
    tiles = []
    for a in unit:
        tile = icons[a]
        tiles.append(tile)
        fs = 12
        plt.text(0, y + 1.1*icon_w, description[a], ha="left", fontsize=fs)
        scale = scales[unit[a]]
        barh = .2
        pre = "$" if a == "profit" else ""
        for col, sys, offset in zip(cols, [sys1, sys2], [.25, .5]):
            yy = y + offset * icon_w
            patchw = sys[a] * barw / scale
            rx = icon_w * 1.1
            patch = Rectangle((rx, yy), patchw, 0.2*icon_w, facecolor=col)
            ax.add_patch(patch)
            plt.text(rx + patchw + 0.125*icon_w, yy + 0.125*icon_w, pre+nice_number(sys[a]), ha="left", va="center", fontsize=fs, fontweight="bold")
        y += icon_h

    img = np.vstack(tiles)
    plt.imshow(img)
    plt.axis('off')
    plt.ylim([0, img.shape[0]])
    plt.xlim([0, icon_w * 8])
    ax.invert_yaxis()


def main():


    sys1 = {
        "profit": 40128,
        "FN": 31,
        "FNWO": 6,
        "FP": 2103,
        "FPWO": 13,
    }

    sys2 = {
        "profit": 20463,
        "FN": 43,
        "FNWO": 3,
        "FP": 3360,
        "FPWO": 6,
    }

    plt.figure(figsize=(10,8))
    comparison(sys1, sys2)
    plt.show()



if __name__ == "__main__":
    main()
