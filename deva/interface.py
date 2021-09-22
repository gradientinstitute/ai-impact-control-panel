"""Python interfaces for displaying and comparing models."""
from deva import elicit
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from os import path

icons = {}  # Icon image cache


def readout(x, info, suffix=False, sigfig=2):
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
    s = info["prefix"] + s.replace(".0", "")

    if suffix:
        s += " " + plural(info["suffix"], x)

    return s


def plural(text, x):
    if (x - 1)**2 < 1e-8:
        s = ""
    else:
        s = "s"
    return text.format(s=s)


def compare(sys1, sys2, meta, attribute):
    """Compare an attribute between two systems."""
    info = meta[attribute]
    v1 = sys1[attribute]
    v2 = sys2[attribute]
    name1 = sys1.name
    # name2 = sys2.name

    rtol = 1.05  # 5% difference
    atol = 0  # single count difference

    diffv = abs(v1-v2)
    diff = readout(diffv, info)
    action = plural(info["action"], v2-v1+1)
    descr = plural(info["description"], diffv)
    focus = "The systems"

    # Which direction is better doesn't matter if the unit format is consistent
    if v1 > v2 * rtol + atol:
        focus = name1
        diff += " " + info["more"]
    elif v2 > v1 * rtol + atol:
        focus = name1
        diff += " " + info["less"]
    else:
        if v1 == v2:
            diff = "the same"
        else:
            diff = "a similar"
        diff += f" {info['countable']} of"

    return f"{focus} {action} {diff} {descr}."


def describe(value, meta, attrib):
    info = meta[attrib]
    v = value[attrib]
    reading = readout(v, info)
    does = info['action'].format(s="s")
    desc = plural(info['description'], v)
    description = f"{value.name} {does} {reading} {desc}"
    return description


def text(value, meta):
    if isinstance(value, elicit.Pair):
        # Display a pairwise comparison
        a, b = value
        print(f"{'Do you prefer?':25s}{a.name:20s}{b.name:20s}")

        for attrib in sorted(a.attributes):
            info = meta[attrib]
            v1 = readout(a[attrib], info, suffix=True)
            v2 = readout(b[attrib], info, suffix=True)
            comparison = compare(value[0], value[1], meta, attrib)
            print(f"{attrib:25s}{v1:20s}{v2:20s}{comparison}")

    elif isinstance(value, elicit.Candidate):
        # Display a single candidate
        print(value.name)

        for attrib in sorted(value.attributes):
            info = meta[attrib]
            v = value[attrib]
            desc = describe(value, meta, attrib)
            reading = readout(v, info, suffix=True)
            print(f"{attrib:25s}{reading:20s}{desc}")


def get_icon(name):
    global icons

    if name not in icons:
        abs_path = path.dirname(path.abspath(__file__))
        icon_path = path.join(abs_path, "icons")
        icon_file = path.join(icon_path, name + ".png")
        img = plt.imread(icon_file)
        icons[name] = img

    return icons[name]


def mpl(value, meta):
    plt.clf()
    if isinstance(value, elicit.Pair):
        sys1, sys2 = value
    elif isinstance(value, elicit.Candidate):
        sys1, sys2 = value, None

    # Layout parameters
    title_x = 7
    title_y = 0
    row_w = 14
    row_h = 2.5
    icon_l = 0.1
    icon_r = 1.4
    text_y = icon_r + 0.25
    name_l = 1.8
    bar_l = 3.5
    bar_w = 8
    readout_l = bar_l + bar_w + 0.1

    if sys2:
        bars = [(sys1, 0.6, 'dark'),
                (sys2, 1.1, 'light')]
    else:
        bars = [(sys1, 0.85, 'normal')]

    bar_h = 0.5  # height of bar

    # Set up an axis
    ax = plt.gca()
    plt.ylim([0, len(sys1.attributes) * row_h])
    plt.xlim([0, row_w])
    ax.set_aspect(1.0)  # keep images square
    plt.axis('off')
    ax.invert_yaxis()

    # Display each attribute in a row
    for row, a in enumerate(sorted(sys1.attributes)):
        y = row * row_h
        plt.text(title_x, title_y + y, a, fontsize=12,
                 va="center", ha="center", fontweight="bold")
        info = meta[a]

        # Draw the icon
        icon = get_icon(info["icon"])
        plt.imshow(icon, extent=(icon_l, icon_r, y + icon_l, y + icon_r),
                   origin="lower")

        # Descriptions
        if sys2:
            text = compare(sys1, sys2, meta, a)
        else:
            text = describe(sys1, meta, a)

        plt.text(title_x, y + text_y, text, fontsize=10, va='center',
                 ha='center')

        # Bar charts
        for sys, offset, shade in bars:
            # Draw the readout
            reading = readout(sys[a], info, suffix=True)
            plt.text(readout_l, y + offset, reading, va='center')
            plt.text(name_l, y + offset, sys.name, fontsize=10, va='center')

            # Draw the bar
            draw_bar(bar_l, y + offset, bar_w, bar_h, sys[a], info, shade)

    # Try to show in a non-blocking way
    plt.tight_layout()
    plt.draw()
    plt.show(block=False)
    plt.pause(0.01)


def draw_bar(x, y, w, h, val, info, shade):
    minv = info['min']
    maxv = info['max']
    pad = 0.1 * (maxv - minv)
    maxv += pad
    minv -= pad
    isgood = info["higherIsBetter"]

    cols = {
        'dark': ('darkgreen', 'darkred'),
        'light': ('springgreen', 'salmon'),
        'normal': ('green', 'red')
    }[shade]

    alpha = (val - minv)/(maxv - minv + 1e-3)
    left = x
    mid = x + w * alpha
    right = x + w
    top = y - h/2

    if isgood:
        plt.plot([mid, right],  [y, y], ":",
                 color=cols[1], linewidth=2, alpha=0.5)
        patch = Rectangle((left, top), (mid-left), h, facecolor=cols[0])
    else:
        plt.plot([left, mid],  [y, y], ":",
                 color=cols[0], linewidth=2, alpha=0.5)
        patch = Rectangle((mid, top), (right-mid), h, facecolor=cols[1])

    plt.gca().add_patch(patch)
