"""Python interfaces for displaying and comparing models."""
from deva import elicit


def readout(x, info, suffix=False, sigfig=2):
    # prep a number for text display
    fmt = f"{{:.{sigfig-1}f}}"

    if not info.get("lowerIsBetter", True):
        x = -x  # flip for display

    # This field is optional
    if info.get("type", "") == "qualitative":
        return fmt.format(x)

    if x > 1e6:
        s = fmt.format(x / 1e6) + "M"
    elif x > 1e3:
        s = fmt.format(x / 1e3) + "K"
    else:
        fmt = f"{{:.{info['displayDecimals']}f}}"
        s = fmt.format(x)  # use natural display

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


def text(value, meta):

    if isinstance(value, tuple):
        # Display a pairwise comparison
        a, b = value
        print(f"{'Do you prefer?':45s}{a.name:17s}{b.name:17s}")

        for attrib in sorted(a.attributes):
            info = meta[attrib]
            v1 = readout(a[attrib], info, suffix=False)
            v2 = readout(b[attrib], info, suffix=False)
            name = info["name"]
            if "(" in name:
                name = name.split("(")[1].split(")")[0]

            print(f"{name:45s}{v1:17s}{v2:17s}")

    elif isinstance(value, elicit.Candidate):
        # Display a single candidate
        print(value.name)

        for attrib in sorted(value.attributes):
            info = meta[attrib]
            reading = readout(value[attrib], info, suffix=False)
            print(f"{info['name']:45s}{reading:17s}")
