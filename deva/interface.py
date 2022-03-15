"""
Python interfaces for displaying and comparing models.

Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
"""

from deva import elicit


def readout(x, info, suffix=False, sigfig=2):
    """Display a metric using its metadata."""
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
    """Format text for singular/plural gramattical numbers."""
    if (x - 1)**2 < 1e-8:
        s = ""
    else:
        s = "s"
    return text.format(s=s)


def text(value, meta):
    """Display a candidate or tuple of candidates in human readable form."""
    lines = []

    if isinstance(value, tuple):
        # Display a pairwise comparison
        # TODO: I dont think this will work for n-tuples
        # TODO: does every system have a spec_name now?
        a, b = value
        lines.append(f"{'':45s}{a.name:17s}{b.name:17s}")

        for attrib in sorted(a.attributes):
            info = meta[attrib]
            v1 = readout(a[attrib], info, suffix=False)
            v2 = readout(b[attrib], info, suffix=False)
            name = info["name"]
            if "(" in name:
                name = name.split("(")[1].split(")")[0]

            lines.append(f"{name:45s}{v1:17s}{v2:17s}")

    elif isinstance(value, elicit.Candidate):
        # Display a single candidate
        lines.append("Display name: " + value.name)
        if value.spec_name != value.name:
            lines.append("Spec name: " + value.spec_name)

        pad = max(len(meta[a]["name"]) for a in value.attributes) + 2
        fmt = f"    {{:{pad}s}}{{:17s}}"

        for attrib in sorted(value.attributes):
            info = meta[attrib]
            reading = readout(value[attrib], info, suffix=False)
            lines.append(fmt.format(info["name"], reading))

    return lines
