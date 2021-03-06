"""
Loading and parsing candidates and metadata.

Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>
"""

import math
import os.path
import os
from glob import glob
from deva import elicit
import toml
from deva.pareto import remove_non_pareto


def repo_root():
    """
    Identify root path of the repository.

    Note - assumes the inplace behaviour of a Poetry install.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def name_from_files(lst):
    """Extract the name from the filename for list of paths."""
    names = {
        "_".join(os.path.splitext(os.path.basename(i))[0].split("_")[1:])
        for i in lst
    }
    return names


def get_all_files(scenario):
    """Ensure all the models have metrics, scores and param files."""
    metric_files = glob(os.path.join(scenario, "models/metrics_*.toml"))
    params_files = glob(os.path.join(scenario, "models/params_*.toml"))

    scored_names = name_from_files(metric_files) \
        .intersection(name_from_files(params_files))

    input_files = {}

    for n in scored_names:
        input_files[n] = {
            "metrics": os.path.join(scenario, f"models/metrics_{n}.toml"),
            "params": os.path.join(scenario, f"models/params_{n}.toml")
        }
    return input_files


def list_scenarios():
    """Examine all the scenario folders and extract their metadata."""
    scenarios = glob(os.path.join(repo_root(), "scenarios/*/"))
    metadata_files = {os.path.basename(os.path.normpath(p)): toml.load(
        os.path.join(p, "metadata.toml")) for p in scenarios}
    return metadata_files


def _load_baseline(scenario):
    # attempt to load the baseline
    scenario_path = os.path.join(repo_root(), "scenarios", scenario)
    baseline_f = os.path.join(scenario_path, "baseline.toml")
    if os.path.exists(baseline_f):
        baseline = toml.load(baseline_f)
    else:
        baseline = {}  # optional
    return baseline


def load_scenario(scenario_name, pfilter=True):
    """Load the metadata and candidates of a specific scenario."""
    # Load all scenario files
    scenario_path = os.path.join(repo_root(), "scenarios", scenario_name)
    print("Scanning ", scenario_path)
    input_files = get_all_files(scenario_path)
    models = {}
    for name, fs in input_files.items():
        fname = fs["metrics"]
        models[name] = toml.load(fname)

    scenario = toml.load(os.path.join(scenario_path, "metadata.toml"))
    assert len(models) > 0, "There are no candidate models."

    baseline = _load_baseline(scenario_name)

    # attempt to load the bounds
    bounds_f = os.path.join(scenario_path, "bounds.toml")
    if os.path.exists(bounds_f):
        bounds = toml.load(bounds_f)
        scenario["bounds"] = bounds

    # Apply lowerIsBetter
    metrics = scenario["metrics"]
    flip = [m for m in metrics if not metrics[m].get("lowerIsBetter", True)]
    for f in flip:
        for val in models.values():
            val[f] = -val[f]

        for i in baseline:
            baseline[i][f] = -baseline[i][f]

    scenario["baseline"] = baseline

    # Filter efficient set
    if pfilter:
        models = remove_non_pareto(models)

    assert len(models) > 0, "There are no efficient models."

    # Convert the TOML-loaded dictionaries into candidate objects.
    candidates = []

    for spec_name, perf in models.items():
        name = elicit.autoname(len(candidates))
        scores = {k: v for k, v in perf.items()}
        candidates.append(elicit.Candidate(name, scores, spec_name))

    inject_metadata(metrics, candidates)

    if "primary_metric" in scenario:
        primary = scenario["primary_metric"]
        if primary not in metrics:
            raise RuntimeError(f"{primary} is not in the scenario metrics.")

    return candidates, scenario


def inject_metadata(metrics, candidates):
    """Inject dynamic metadata after looking at candidates."""
    for attr, meta in metrics.items():

        # Fill defaults
        if "type" not in meta:
            meta["type"] = "quantitative"

        # calculate the attribute range spanned by the candidates
        meta["min"] = min(c[attr] for c in candidates)
        meta["max"] = max(c[attr] for c in candidates)

        # defaults for visual min and max
        if "visual_min" not in meta:
            meta["visual_min"] = meta["min"]

        if "visual_max" not in meta:
            meta["visual_max"] = meta["max"]

        # compensate higher is better
        if "lowerIsBetter" not in meta:
            meta["lowerIsBetter"] = True

        if not meta["lowerIsBetter"]:
            if "range_min" in meta and "range_max" in meta:
                # flip the min and max
                range_min = meta["range_min"]
                range_max = meta["range_max"]
                meta["range_min"] = -range_max
                meta["range_max"] = -range_min

            elif "range_max" in meta:
                meta["range_min"] = -meta["range_max"]
                del meta["range_max"]

            elif "range_min" in meta:
                meta["range_max"] = -meta["range_min"]
                del meta["range_min"]

        if meta["type"] == "quantitative":
            meta["displayDecimals"] = int(meta["displayDecimals"])

            if candidates:
                # the user may set fixed ranges with nice defaults if they dont
                (range_min, range_max) = nice_range(meta["min"], meta["max"])
            else:
                raise Exception("Sorry, there is no candidate model.")

            if "range_min" not in meta:
                meta["range_min"] = range_min
            if "range_max" not in meta:
                meta["range_max"] = range_max

        elif meta["type"] == "qualitative":
            meta["displayDecimals"] = None

        else:
            raise Warning(f"Data type {meta['type']} not supported.")


def nice_range(a, b):
    """
    Round min down and max up to the nearest `div`.

    Return the minimum value and the maximum value in order in a tuple.
    """
    min_num = min(a, b)
    max_num = max(a, b)
    diff = math.ceil(max_num - min_num)
    div = 10**(len(str(diff)) - 1)

    if min_num % div == 0:
        min_num -= div
    if max_num % div == 0:
        max_num += div
    min_num = math.floor(min_num / div) * div
    max_num = math.ceil(max_num / div) * div
    return (min_num, max_num)
