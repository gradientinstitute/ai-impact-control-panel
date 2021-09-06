import os.path
from glob import glob


def name_from_files(lst):
    """Extract the name from the filename for list of paths"""
    names = set([
        os.path.splitext(os.path.basename(i))[0].split('_')[-1]
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
