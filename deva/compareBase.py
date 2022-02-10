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

    for m in bounds:
        if metrics[m]["type"] == "quantitative":
            report += m + "\n"
            for ref in baseline:
                val = bounds[m]
                refVal = baseline[ref][m]
                lowerIsBetter = metrics[m]["lowerIsBetter"]

                report += ref + ": " + metrics[m]["description"][:-1]

                if val[1] < refVal:  # reference not in range
                    if lowerIsBetter:
                        report += " is too high.\n"
                    else:
                        report += " is too low.\n"
                else:
                    report += " is within the boundaries.\n"

    return report
