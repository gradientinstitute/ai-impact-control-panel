import os.path
import os
import shutil
from glob import glob
from deva import elicit
import toml
from deva.pareto import remove_non_pareto


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def name_from_files(lst):
    """Extract the name from the filename for list of paths"""
    names = set([
        "_".join(os.path.splitext(os.path.basename(i))[0].split('_')[1:])
        for i in lst])
    return names


def get_all_files(scenario):
    """Ensure all the models have metrics, scores and param files"""
    metric_files = glob(os.path.join(scenario, "models/metrics_*.toml"))
    params_files = glob(os.path.join(scenario, "models/params_*.toml"))

    scored_names = name_from_files(metric_files) \
        .intersection(name_from_files(params_files))

    input_files = dict()

    for n in scored_names:
        input_files[n] = {
                'metrics': os.path.join(scenario, f'models/metrics_{n}.toml'),
                'params': os.path.join(scenario, f'models/params_{n}.toml')
                }
    return input_files


def autoname(ind):
    # sequence A-Z, AA-AZ-ZZ, AAA-AAZ-AZZ-ZZZ ...
    chars = []
    while True:
        chars.append(chr(65 + ind % 26))
        if ind < 26:
            break
        ind = ind // 26 - 1
    return "System " + "".join(chars[::-1])


def list_scenarios():
    scenarios = glob(os.path.join(repo_root(), 'scenarios/*/'))
    metadata_files = {os.path.basename(os.path.normpath(p)): toml.load(
        os.path.join(p, "metadata.toml")) for p in scenarios}
    return metadata_files


def load_baseline(scenario):
    # attempt to load the baseline
    scenario_path = os.path.join(repo_root(), 'scenarios', scenario)
    baseline_f = os.path.join(scenario_path, "baseline.toml")
    assert os.path.exists(baseline_f)
    baseline = toml.load(baseline_f)
    return baseline


def load_scenario(scenario_name, pfilter=True):
    # Load all scenario files
    scenario_path = os.path.join(repo_root(), 'scenarios', scenario_name)
    print("Scanning ", scenario_path)
    input_files = get_all_files(scenario_path)
    models = {}
    for name, fs in input_files.items():
        fname = fs['metrics']
        models[name] = toml.load(fname)

    scenario = toml.load(os.path.join(scenario_path, "metadata.toml"))

    assert len(models) > 0, "There are no candidate models."

    # Filter efficient set
    if pfilter:
        models = remove_non_pareto(models, scenario)

    assert len(models) > 0, "There are no candidate models after filtering."

    # Convert the TOML-loaded dictionaries into candidate objects.
    candidates = []
    metrics = scenario["metrics"]

    for spec_name, perf in models.items():
        name = autoname(len(candidates))
        scores = {k: v for k, v in perf.items()}
        candidates.append(elicit.Candidate(name, scores, spec_name))

    for u in metrics:
        metrics[u]["max"] = max(c[u] for c in candidates)
        metrics[u]["min"] = min(c[u] for c in candidates)
        metrics[u]["decimals"] = int(metrics[u]["decimals"])
        if "countable" not in metrics[u]:
            # auto-fill optional field
            metrics[u]["countable"] = (
                "number" if metrics[u]["decimals"] == 0 else "amount")

    if 'primary_metric' in scenario:
        primary = scenario['primary_metric']
        if primary not in metrics:
            raise RuntimeError(f'{primary} is not in the scenario metrics.')

    scenario["baseline"] = load_baseline(scenario_name)
    return candidates, scenario

