"""
Generate the report shown in the frontend.

Date: Feb 10, 2022
Author: Muyao Chen
"""


def compare(meta, baseline, bounds):
    """
    Compare baselines against the boundaries.

    For each reference, report whether they meet the current bounds,
    and if they don't, identify why not.

    Parameters
    ----------
    baseline: dict
    {
      "inaction": {metrics: value}
      "industry_average": {metrics: value}
    }

    bounds: dict
    {metrics: [min_value, max_value]}

    Returns
    -------
    report: string

    """
    report = ""
    metrics = meta["metrics"]

    for ref in baseline:
        report += ref
        reason = ""
        accept = True

        for m in bounds:
            if metrics[m]["type"] == "quantitative":
                val = bounds[m]
                refVal = baseline[ref][m]
                print(val)
                if val[1] < refVal:  # reference not in range
                    accept = False
                    lowerIsBetter = metrics[m]["lowerIsBetter"]
                    description = metrics[m]["name"]

                    if lowerIsBetter:
                        reason += description + " is too high.\n"
                    else:
                        reason += description + " is too low.\n"

        if accept:
            report += " is acceptable.\n"
        else:
            report += " is unacceptable because of the following reason(s)\n"
            report += reason

    return report
