import click
import toml
import numpy as np
import pandas as pd
from deva.elicit import Toy
import logging
from deva.pareto import remove_non_pareto
from deva import fileio


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
    input_files = fileio.get_all_files(scenario)

    models = {}
    for name, fs in input_files.items():
        fname = fs['metrics']
        models[name] = toml.load(fname)

    models = remove_non_pareto(models)

    models = remove_unacceptable(models)
    if len(models) == 0:
        print("There are no acceptable candidates.")
        return


    # Give all the models easy to remember names.... [optionally]
    tmp = {}
    for i, model in enumerate(models.values()):
        tmp["System " + chr(65+i)] = model
    models = tmp

    eliciter = Toy(models)
    while not eliciter.finished():
        (m1, m1perf), (m2, m2perf) = eliciter.prompt()
        print("Which model do you prefer:\n")
        pretty_print_performance(m1, m1perf)
        pretty_print_performance(m2, m2perf)
        print(f'(Answer {m1} or {m2})')
        print('> ', end='')
        i = input()
        choice = eliciter.user_input("System " + i)
        if choice is not None:
            print(f'You preferred model {choice}')
        else:
            print('Invalid selection, please try again.')
    result_name, result = eliciter.final_output()
    print('\n\nSelection complete.' +
          ' Based on your preferences you have selected:\n')
    pretty_print_performance(result_name, result)


def get_scores_df(models):
    # Create list of metric names
    sample_model = models[next(iter(models))]
    metrics = [met_name for met_name in iter(sample_model)]
    metric_type = [met_type["type"] for met_type in sample_model.values()]

    model_ids = []
    scores = np.zeros((len(models), len(metrics)))
    
    # Make array of scores
    for i, (model_id, model_scores) in enumerate(models.items()):
        model_ids.append(model_id)
        for j, metric in enumerate(model_scores.values()):
            scores[i, j] = metric["score"]

    scores_df = pd.DataFrame(scores, columns=metrics)
    scores_df["model_id"] = np.array(model_ids)
    scores_df.set_index("model_id", inplace=True)

    # change int metrics to type int
    int_metrics = [m_name for m_name, m_type in 
                    zip(metrics, metric_type) if m_type == "int"]
    scores_df[int_metrics] = scores_df[int_metrics].astype(int)

    return scores_df

def get_optimals(models):
    
    sample_model = models[next(iter(models))]
    metrics = [met_name for met_name in iter(sample_model)]
    metric_optimals = [met_type["optimal"] for met_type in sample_model.values()]

    met_optimal_dict = {met_name: met_opt for met_name, met_opt 
                        in zip(metrics, metric_optimals)}
    return met_optimal_dict

def remove_unacceptable(models):
    # Create DataFrame of metrics and model scores
    scores_df = get_scores_df(models)
    metric_optimals = get_optimals(models)
    # Show best case and worst case?
    print("\nShow candidates? y or [n]:")
    print('> ', end='')
    show_cand = input()
    if show_cand == "y":
        print(scores_df)

    print("\nInput the worst acceptable value for each metric.")
    for met_name, met_opt in metric_optimals.items():

        if met_opt == "min":
            print("Max acceptable {} :".format(met_name))
            print('> ', end='')
            i = input()
            unaccept_bool = scores_df[met_name] > float(i)
        elif met_opt == "max":
            print("Min acceptable {} :".format(met_name))
            print('> ', end='')            
            i = input()
            unaccept_bool = scores_df[met_name] < float(i)
        else:
            print('Optimal value for metric should be either "max" or "min".')
        print("Removing {} unacceptable models".format(np.sum(unaccept_bool)))
        scores_df = scores_df[~unaccept_bool]
    
    models = {m_i: models[m_i] for m_i in scores_df.index}
    return models