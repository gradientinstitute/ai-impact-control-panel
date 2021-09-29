import os.path
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


def load_scenario(scenario, bounds):
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

    for perf in models.values():
        # TODO: retain "special" names of reference models.
        name = "System " + chr(65 + len(candidates))
        scores = {name2id[k]: v['score'] for k, v in perf.items()}
        candidates.append(elicit.Candidate(name, scores))

    for u in metrics:
        metrics[u]["max"] = max(c[u] for c in candidates)
        metrics[u]["min"] = min(c[u] for c in candidates)
        metrics[u]["decimals"] = int(metrics[u]["decimals"])
        metrics[u]["countable"] = (
            "number" if metrics[u]["decimals"] == 0 else "amount")

    return candidates, scenario
