"""
Functions to help user remove unacceptable models.
"""
import numpy as np
import pandas as pd


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

        # Check that some candidates remain in the set.
        if scores_df.shape[0] == 0:
            print("No candidates remain to choose from.")
            break

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
                raise

            temp_scores_df = scores_df[~unaccept_bool]
            if len(temp_scores_df) == 0:
                print("WARNING: This limit will remove all candidates.")

            elif show_cand == "y":
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


def pretty_print_dict(d):
    for k in d.keys():
        try:
            if np.issubdtype(d[k], np.integer):
                print(f'\t{k}: {d[k]}')
            elif np.issubdtype(d[k], np.float):
                print(f'\t{k}: {d[k]:0.2f}')
        except Exception:
            print("No candidates remain.")

    print('\n')
