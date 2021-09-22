"""Python interfaces for displaying and comparing models."""
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