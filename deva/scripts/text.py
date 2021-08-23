import click
import toml
from deva.elicit import Toy
import os
import logging
import numpy as np
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


def pretty_print_performance(name, d):
    print(f'Model {name}:')
    for k in sorted(d.keys()):
        print(f'\t{k}: {d[k]:0.2f}')
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


    # Check if model is bested by another in every metric
    print("Remove models not on the pareto front")
    non_pareto = []
    for i, m in enumerate(models):
        for r in models:
            if np.all(np.array(list(models[m].values())) < np.array(list(models[r].values()))):
                non_pareto.append(m)
                # print(models[m])
                # print(models[r])
                break
    
    # Delete all models that aren't on the pareto front
    for m in non_pareto:
        del models[m]


    eliciter = Toy(models)
    while not eliciter.finished():
        (m1, m1perf), (m2, m2perf) = eliciter.prompt()
        print("Which model do you prefer:\n")
        pretty_print_performance(m1, m1perf)
        pretty_print_performance(m2, m2perf)
        print(f'(Answer {m1} or {m2})') 
        print('> ', end='')
        i = input()
        choice = eliciter.user_input(i)
        if choice is not None:
            print(f'You preferred model {choice}')
        else:
            print('Invalid selection, please try again.')
    result_name, result = eliciter.final_output()
    print('\n\nSelection complete.' +
          ' Based on your preferences you have selected:\n')
    pretty_print_performance(result_name, result)
