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


def _load_baseline(scenario):
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

    baseline = _load_baseline(scenario_name)

    # Apply lowerIsBetter
    metrics = scenario["metrics"]
    flip = [m for m in metrics if not metrics[m].get('lowerIsBetter', True)]
    for f in flip:
        for val in models.values():
            val[f] = -val[f]

        baseline[f] = -baseline[f]

    scenario["baseline"] = baseline

    # Filter efficient set
    if pfilter:
        models = remove_non_pareto(models)

    assert len(models) > 0, "There are no efficient models."

    # Convert the TOML-loaded dictionaries into candidate objects.
    candidates = []

    for spec_name, perf in models.items():
        name = autoname(len(candidates))
        scores = {k: v for k, v in perf.items()}
        candidates.append(elicit.Candidate(name, scores, spec_name))

    load_all_metrics(metrics, candidates)

    if 'primary_metric' in scenario:
        primary = scenario['primary_metric']
        if primary not in metrics:
            raise RuntimeError(f'{primary} is not in the scenario metrics.')

    return candidates, scenario


def load_all_metrics(metrics, candidates):
    for u in metrics:
        if "type" not in metrics[u]:
            # set default type
            metrics[u]["type"] = "quantitative"

        if metrics[u]["type"] == "qualitative":
            load_qualitative_metric(metrics, candidates, u)
        elif metrics[u]["type"] == "quantitative":
            load_quantitative_metric(metrics, candidates, u)


def load_qualitative_metric(metrics, candidates, u):
    metrics[u]["max"] = max(c[u] for c in candidates)
    metrics[u]["min"] = min(c[u] for c in candidates)
    if "lowerIsBetter" not in metrics[u]:
        metrics[u]["lowerIsBetter"] = True


def load_quantitative_metric(metrics, candidates, u):
    metrics[u]["max"] = max(c[u] for c in candidates)
    metrics[u]["min"] = min(c[u] for c in candidates)
    metrics[u]["display-decimals"] = int(metrics[u]["display-decimals"])
    if "countable" not in metrics[u]:
        # auto-fill optional field
        metrics[u]["countable"] = (
            "number" if metrics[u]["display-decimals"] == 0 else "amount")
    if "lowerIsBetter" not in metrics[u]:
        metrics[u]["lowerIsBetter"] = True


def delete_files(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
