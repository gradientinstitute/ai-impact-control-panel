import click
import toml
from deva.elicit import Toy
import os
import logging
# import numpy as np
from deva.pareto import remove_non_pareto
from glob import glob
import matplotlib.pyplot as plt
from deva.vis import comparison


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


def pretty_print_performance(name, d):
    print(f'Model {name}:')
    for k in sorted(d.keys()):
        if d[k]["type"] == "int":
            print(f'\t{k}: {d[k]["score"]}')
        else:
            print(f'\t{k}: {d[k]["score"]:0.2f}')
    print('\n')


@click.command()
@click.argument('scenario', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def cli(scenario):
    logging.basicConfig(level=logging.INFO)
    input_files = get_all_files(scenario)

    models = {}
    for name, fs in input_files.items():
        fname = fs['metrics']
        models[name] = toml.load(fname)

    models = remove_non_pareto(models)

    # icon_key = ["profit", "FNWO", "FPWO", "FP", "FN", "CORRECT", "INCORRECT"]
    remap = {
        'False Positives': 'FP',
        'False Negatives': 'FN',
        'People with >=3 FN': 'FNWO',
        'People with >=5 FP': 'FPWO',
        'Net profit': 'profit'
    }
    maxima = {}

    # Give all the models easy to remember names.... [optionally]
    tmp = {}
    for i, model in enumerate(models.values()):
        tmp["System " + chr(65+i)] = model
    models = tmp

    # compute set-wide maxima  - assuming positive for demo purposes
    for model in models.values():
        for k, v in model.items():
            a = remap[k]
            maxima[a] = max(maxima.get(a, 0), v["score"])

    eliciter = Toy(models)
    plt.figure(figsize=(10, 8))
    plt.ion()

    while not eliciter.finished():
        (m1, m1perf), (m2, m2perf) = eliciter.prompt()

        # patch into the visualisation
        sys1 = {remap[k]: m1perf[k]["score"] for k in remap}
        sys2 = {remap[k]: m2perf[k]["score"] for k in remap}
        sys1["name"] = m1
        sys2["name"] = m2

        plt.clf()
        # plt.gcf().set_size_inches(10, 8)
        comparison(sys1, sys2, scale=maxima)
        plt.draw()
        plt.pause(0.01)

        print("Which model do you prefer:\n")
        m1 = m1.split()[-1]  # just A or B
        m2 = m2.split()[-1]
        print(f'(Answer {m1} or {m2})')
        print('> ', end='')
        i = input()
        choice = eliciter.user_input("System " + i)
        if choice is not None:
            print(f'You preferred model {choice}')
        else:
            print('Invalid selection, please try again.')
    result_name, result = eliciter.final_output()
    print('\n\nYou have selected:', result_name)
    # pretty_print_performance(result_name, result)

    plt.clf()
    sys1 = {remap[k]: result[k]["score"] for k in remap}
    sys1["name"] = result_name
    comparison(sys1, None, scale=maxima)
    plt.show()
