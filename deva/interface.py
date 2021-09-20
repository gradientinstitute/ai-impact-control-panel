"""Designed to behave a bit like a web front-end in terms of receiving a data
package and displaying it."""
from deva import elicit


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
         s += " " + info["suffix"].format(s=auto_s(x))

    return s


def auto_s(x):
    if (x - 1)**2 < 1e-8:
        s = ""
    else:
        s = "s"
    return s



def compare(sys1, sys2, meta, attribute):
    """Compare an attribute between two systems."""
    info = meta[attribute]
    v1 = sys1[attribute]
    v2 = sys2[attribute]
    name1 = sys1.name
    name2 = sys2.name
    action = info["action"]
    desc = info["description"]
    diffv = abs(v1-v2)
    diff = readout(diffv, info)

    rtol = 1.05  # 5% difference
    atol = 0  # single count difference

    # Which direction is better doesn't matter if the unit format is consistent
    if v1 > v2 * rtol + atol:
        focus = name1
        action = action.format(s="s")
        diff += " " + info["more"]
    elif v2 > v1 * rtol + atol:
        focus = name1
        action = action.format(s="s")
        diff += " " + info["less"]
    else:
        focus = "The systems"
        if v1 == v2:
            diff = "the same"
        else:
            diff = "a similar"
        diff += f" {info['countable']} of"
        action = action.format(s="")

    descr = desc.format(s=auto_s(diffv))
    return f"{focus} {action} {diff} {descr}."


def text(value, meta):
        if isinstance(value, elicit.Pair):
            # Ask a pairwise comparison
            a, b = value
            text = f"{'Do you prefer?':25s}{a.name:20s}{b.name:20s}\n"

            for attrib in sorted(a.attributes):
                info = meta[attrib]
                v1 = readout(a[attrib], info, suffix=True)
                v2 = readout(b[attrib], info, suffix=True)
                comparison = compare(value[0], value[1], meta, attrib)
                text += f'{attrib:25s}{v1:20s}{v2:20s}{comparison}\n'

            print(text)

        elif isinstance(value, elicit.Candidate):
            # Display a single candidate
            text = f'{value.name}:\n'
            for attrib in sorted(value.attributes):
                info = meta[attrib]
                v = value[attrib]
                reading = readout(v, info)
                does = info['action'].format(s="s")
                shc = (f"{value.name} {does} {reading} " +
                       f"{info['description'].format(s=auto_s(v))}")
                reading = readout(v, info, suffix=True)
                text += f"{attrib:25s}{reading:20s}{shc}\n"

            print(text)



# def mpl(value, meta):
#         print
    # plt.clf()
    # comparison(sys1, sys2, scale=maxima)  # remap=remap
    # plt.draw()
    # plt.show(block=False)
    # plt.pause(0.01)

    # plt.clf()
    # comparison(sys1, None, scale=maxima)  # remap=remap
    # plt.draw()
    # plt.pause(0.1)
    # input()

