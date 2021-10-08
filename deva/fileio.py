import os.path
import os
import shutil
from glob import glob
from deva import elicit
import toml
from deva.pareto import remove_non_pareto
from deva.bounds import remove_unacceptable


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def name_from_files(lst):
    """Extract the name from the filename for list of paths"""
    names = set([
        "_".join(os.path.splitext(os.path.basename(i))[0].split('_')[-2:])
        for i in lst])
    return names


def get_all_files(scenario):
    """Ensure all the models have metrics, scores and param files"""
    scored_files = glob(os.path.join(scenario, "models/scored_*.csv"))
    metric_files = glob(os.path.join(scenario, "models/metrics_*.toml"))
    params_files = glob(os.path.join(scenario, "models/params_*.toml"))

    scored_names = name_from_files(scored_files) \
        .intersection(name_from_files(metric_files)) \
        .intersection(name_from_files(params_files))

    input_files = dict()

    for n in scored_names:
        input_files[n] = {
                'scores': os.path.join(scenario, f'models/scored_{n}.csv'),
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


def load_scenario(scenario, bounds, pfilter=True):
    # Load all scenario files
    scenario_path = os.path.join(repo_root(), 'scenarios', scenario)
    print("Scanning ", scenario_path)
    input_files = get_all_files(scenario_path)
    models = {}
    for name, fs in input_files.items():
        fname = fs['metrics']
        models[name] = toml.load(fname)

    scenario = toml.load(os.path.join(scenario_path, "metadata.toml"))

    # Filter efficient set
    if pfilter:
        models = remove_non_pareto(models)

    # TODO: Simon's remove_unacceptable is here temporarily.
    # It's on the issue stack to update it to work with candidate objects.
    if bounds:
        models = remove_unacceptable(models)

    assert len(models) > 0, "There are no candidate models."

    # Convert the TOML-loaded dictionaries into candidate objects.
    candidates = []
    metrics = scenario["metrics"]

    # TODO: change format upstream to remove metadata from model score files.
    # TODO: change the data-gen code so fields match id not name
    # For now we can adapt them
    name2id = {metrics[uid]["name"]: uid for uid in metrics}

    for spec_name, perf in models.items():
        name = autoname(len(candidates))
        scores = {name2id[k]: v['score'] for k, v in perf.items()}
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

    return candidates, scenario


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
