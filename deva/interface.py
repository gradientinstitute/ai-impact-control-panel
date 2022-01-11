"""Python interfaces for displaying and comparing models."""
from deva import elicit


def readout(x, info, suffix=False, sigfig=2):
    # prep a number for text display
    fmt = f"{{:.{sigfig-1}f}}"

    # This field is optional
    if info.get("type", "") == "qualitative":
        return fmt.format(x)

    if x > 1e6:
        s = fmt.format(x/1e6) + "M"
    elif x > 1e3:
        s = fmt.format(x/1e3) + "K"
    else:
        fmt = f"{{:.{info['display-decimals']}f}}"
        s = fmt.format(x)  # use natrual display

    s = info["prefix"] + s

    if suffix and len(info["suffix"]) < 20:
        # how are the suffixes getting so huge?
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
    action = info["action"].format(s="")
    # The text translations no longer make sense...
    # descr = plural(info["description"], diffv)
    name = info['name'].lower()
    if '(' in name:
        name = name.split('(')[1].split(')')[0]

    descr = name + " " + info["suffix"]  # heuristic repair
    focus = "The systems"

    # Which direction is better doesn't matter if the unit format is consistent
    if v1 > v2 * rtol + atol:
        focus = name1
        action = info["action"].format(s="s")  # single focus system
        diff += " " + info["more"]
    elif v2 > v1 * rtol + atol:
        focus = name1
        diff += " " + info["less"]
        action = info["action"].format(s="s")  # single focus system
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


# def get_lengths(a, meta):
#     # the length of these strings is unsuitable for console output
#     # Figure out table size actively
#     infos = [meta[at] for at in a.attributes]
#     a_width = max(len(i['name']) for i in infos)
#     s_width = max(len(i['suffix']) for i in infos)
#     p_width = max(len(meta[attr]['prefix']) for attr in a.attributes)


def text(value, meta):

    if isinstance(value, elicit.Pair):
        # Display a pairwise comparison
        a, b = value
        print(f"{'Do you prefer?':45s}{a.name:17s}{b.name:17s}")

        for attrib in sorted(a.attributes):
            info = meta[attrib]
            v1 = readout(a[attrib], info, suffix=False)
            v2 = readout(b[attrib], info, suffix=False)
            # comparison = compare(value[0], value[1], meta, attrib)
            name = info['name']
            if '(' in name:
                name = name.split('(')[1].split(')')[0]

            # print(f"{name:25s}{v1:20s}{v2:20s}{comparison}")
            # these names are getting too long!
            print(f"{name:45s}{v1:17s}{v2:17s}")

    elif isinstance(value, elicit.Candidate):
        # Display a single candidate
        print(value.name)  # spec_name is retired?
        # print(f'{value.name} ({value.spec_name})')

        for attrib in sorted(value.attributes):
            info = meta[attrib]
            v = value[attrib]
            # desc = describe(value, meta, attrib)
            reading = readout(v, info, suffix=False)
            print(f"{info['name']:45s}{reading:17s}")
            # {desc}")  # descriptions are now broken
