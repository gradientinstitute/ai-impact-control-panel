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


def pretty_print_dict(d):
    for k in d.keys():
        if np.issubdtype(d[k], np.integer):
            print(f'\t{k}: {d[k]}')
        else:
            print(f'\t{k}: {d[k]:0.2f}')
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

    # Allow user to define acceptable region and remove models outside of that
    print("\nDefine region of acceptability? y or [n]")
    print('> ', end='')
    i = input()
    if i == "y":
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
    # Make a pandas dataframe of the model scores
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
    # Return a dict of metric keys and values that specify
    # whether its better to maximises or minimise the metric.
    sample_model = models[next(iter(models))]
    metrics = [met_name for met_name in iter(sample_model)]
    metric_optimals = [met_type["optimal"] for
                       met_type in sample_model.values()]

    met_optimal_dict = {met_name: met_opt for met_name, met_opt
                        in zip(metrics, metric_optimals)}
    return met_optimal_dict


def remove_unacceptable(models):
    # Create DataFrame of metrics and model scores
    scores_df = get_scores_df(models)
    metric_optimals = get_optimals(models)
    orig_scores_df = scores_df.copy()

    # Show available models scores as a guide to the user?
    print("\nShow changes to set of available candidates? y or [n]:")
    print('> ', end='')
    show_cand = input()
    if show_cand == "y":
        scores_summary(scores_df, metric_optimals)

    print("\nInput the worst acceptable value for each metric.")
    for met_name, met_opt in metric_optimals.items():
        while True:  # Loop allows user to rethink a limit they just proposed

            # Ask user for input
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
                print('Optimal value for metric should be' +
                      'either "max" or "min".')

            temp_scores_df = scores_df[~unaccept_bool]
            if show_cand == "y":
                # Show text-based image of metrics ranges in the candidate set
                text_range_plots(orig_scores_df, scores_df,
                                 temp_scores_df)

            print("\nDo you wish to implement this limit? y or [n]")
            print('> ', end='')
            i = input()
            if i == "y":
                print("Removing {}".format(np.sum(unaccept_bool)) +
                      " unacceptable models")
                scores_df = scores_df[~unaccept_bool]
                break

        scores_summary(scores_df, metric_optimals)

    # Make model dict from dataframe
    models = {m_i: models[m_i] for m_i in scores_df.index}
    return models


def scores_summary(scores_df, metric_optimals):
    ideal = {}
    nadir = {}
    for m_name, m_opt in metric_optimals.items():
        if m_opt == "max":
            ideal[m_name] = np.max(scores_df[m_name])
            nadir[m_name] = np.min(scores_df[m_name])
        elif m_opt == "min":
            ideal[m_name] = np.min(scores_df[m_name])
            nadir[m_name] = np.max(scores_df[m_name])
        else:
            print("Metric optimal must be a max or min.")
    print("\nBest achievable values:")
    pretty_print_dict(ideal)
    print("\nWorst achievable values:")
    pretty_print_dict(nadir)


def text_range_plots(orig_scores_df, scores_df, temp_scores_df):
    # Plots range of possible metric values in the candidate set
    n_removed = scores_df.shape[0] - temp_scores_df.shape[0]
    print("\n\nProposed limit removes {}".format(n_removed) +
          " of {} ".format(scores_df.shape[0]) +
          "remaining candiates.")
    for i, metric in enumerate(scores_df):
        orig_min = np.min(orig_scores_df[metric])
        orig_max = np.max(orig_scores_df[metric])

        scores_min = np.min(scores_df[metric])
        scores_max = np.max(scores_df[metric])

        temp_min = np.min(temp_scores_df[metric])
        temp_max = np.max(temp_scores_df[metric])

        if np.issubdtype(temp_max, np.integer):
            print("\n{}.".format(metric) +
                  "\nProposed min: {} (was {}).".format(temp_min, scores_min) +
                  "Proposed max: {} (was {}).".format(temp_max, scores_max))
        else:
            print("\n{}.".format(metric) +
                  "\nProposed min: {:0.2f} (was {:0.2f}).".format(temp_min,
                                                                  scores_min) +
                  "Proposed max: {:0.2f} (was {:0.2f}).".format(temp_max,
                                                                scores_max))

        orig_range = orig_max - orig_min
        tick_size = orig_range / 100

        # Calculate number of left dashes
        scores_start = scores_min - orig_min
        left_dashes = np.round(scores_start / tick_size).astype(int)

        # Calculate number of left x's
        temp_start = temp_min - scores_min
        left_xs = np.round(temp_start / tick_size).astype(int)

        # Calculate number of left oh's
        temp_range = temp_max - temp_min
        ohs = np.round(temp_range / tick_size).astype(int)

        # Calculate number of right x's
        right_xs = np.round((scores_max - temp_max) / tick_size).astype(int)

        # Calculate number of right dashes
        right_dashes = np.round((orig_max - scores_max) /
                                tick_size).astype(int)

        print(("." * left_dashes) + ("-" * left_xs) +
              ("o" * ohs) + ("-" * right_xs) + ("." * right_dashes))
