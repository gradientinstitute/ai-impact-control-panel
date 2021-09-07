import click
from deva.config import parse_config
from deva.model import iter_models
import os
from deva.datasim import simulate
import logging
from logging import info
import pandas as pd
import numpy as np
from joblib import dump
import toml


@click.group()
@click.argument('scenario', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.pass_context
def cli(ctx, scenario):
    ctx.ensure_object(dict)
    logging.basicConfig(level=logging.INFO)
    ctx.obj['folder'] = scenario


@cli.command()
@click.pass_context
def data(ctx):
    folder = ctx.obj['folder']
    data_folder = os.path.join(folder, 'data')
    os.makedirs(data_folder, exist_ok=True)
    sim_cfg_fname = os.path.join(folder, 'sim.toml')
    with open(sim_cfg_fname, 'r') as f:
        sim_cfg = parse_config(f)
    X_train, X_test = simulate(sim_cfg)
    fname_train = 'train.csv'
    fname_test = 'test.csv'
    X_train.to_csv(os.path.join(data_folder, fname_train))
    info(f"saved {fname_train}")
    X_test.to_csv(os.path.join(data_folder, fname_test))
    info(f"saved {fname_test}")


@cli.command()
@click.pass_context
def model(ctx):
    folder = ctx.obj['folder']
    data_folder = os.path.join(folder, 'data')
    model_folder = os.path.join(folder, 'models')
    os.makedirs(model_folder, exist_ok=True)
    model_cfg_fname = os.path.join(folder, 'model.toml')
    with open(model_cfg_fname, 'r') as f:
        cfg = parse_config(f, build_tuple=False)
    fname_train = os.path.join(data_folder, 'train.csv')
    fname_test = os.path.join(data_folder, 'test.csv')

    # Load train data
    df = pd.read_csv(fname_train)
    df.set_index('trans_id', inplace=True)
    X_train = df.drop(['trans_time', 'is_fraud'], axis=1)
    y_train = df.is_fraud
    t_train = df.trans_time

    # Load validation data
    df_val = pd.read_csv(fname_test)
    df_val.set_index('trans_id', inplace=True)
    X_test = df_val.drop(['trans_time', 'is_fraud'], axis=1)
    y_test = df_val.is_fraud
    t_test = df_val.trans_time

    for out in iter_models(X_train, y_train,
                           t_train, X_test,
                           y_test, t_test, cfg):
        name = out['name']
        model_fname = os.path.join(model_folder, f'model_{name}.joblib')
        out_fname = os.path.join(model_folder, f'scored_{name}.csv')
        metric_fname = os.path.join(model_folder, f'metrics_{name}.toml')
        param_fname = os.path.join(model_folder, f'params_{name}.toml')

        data_out = X_test.copy()
        data_out['is_fraud'] = y_test
        data_out['score'] = out['y_scores']
        data_out['is_flagged'] = out['y_pred']
        data_out = data_out.join(t_test)
        data_out.sort_index(inplace=True)
        data_out.to_csv(out_fname)

        dump(out['model'], model_fname)

        with open(metric_fname, 'w') as f:
            toml.dump(out['model_scores'], f,
                      encoder=toml.TomlNumpyEncoder())

        with open(param_fname, 'w') as f:
            toml.dump(out['params'], f,
                      encoder=toml.TomlNumpyEncoder())

        info(f'written model {name}')


@cli.command()
@click.pass_context
def pareto(ctx):
    folder = ctx.obj['folder']
    model_folder = os.path.join(folder, 'models')


    
    os.makedirs(model_folder, exist_ok=True)
    delete_old_models = True
    if delete_old_models:
        delete_files(model_folder)

    model_cfg_fname = os.path.join(folder, 'model.toml')
    with open(model_cfg_fname, 'r') as f:
        cfg = parse_config(f, build_tuple=False)

    n_models = cfg["n_models"]
    n_metrics = len(cfg["metrics"])

    #Sample the hypersphere
    samples = np.random.rand(n_models, n_metrics)
    r = np.sqrt(np.sum(samples**2, axis=1))[:, np.newaxis]
    norm_samples = (1/r) * samples
    metric_values = norm_samples.copy()
    # Transform samples to reflect metric ranges
    for i, m_details in enumerate(cfg["metrics"].values()):
        if m_details["range"][1] < m_details["range"][0]:
            norm_samples[:, i] *= -1
        scale = m_details["range"][1] - m_details["range"][0]
        metric_values[:, i] *= scale
        metric_values[:, i] += m_details["range"][0]



        
    metric_scores = {}
    for model in range(n_models):
        metric_fname = os.path.join(model_folder, f'metrics_{model}.toml')
        out_fname = os.path.join(model_folder, f'scored_{model}.csv')
        param_fname = os.path.join(model_folder, f'params_{model}.toml')
        # Remove

        for i, m_details in enumerate(cfg["metrics"].values()):
            score = metric_values[model, i]
            if m_details["type"] == "int":
                score = int(score)
            metric_scores[m_details["name"]] = {"score": score,
                                                "optimal": m_details["optimal"],
                                                "type": m_details["type"]}

 


        with open(metric_fname, 'w') as f:
            toml.dump(metric_scores, f,
                      encoder=toml.TomlNumpyEncoder())

        with open(out_fname, 'w') as f:
            toml.dump({"Place": "Holder"}, f,
                      encoder=toml.TomlNumpyEncoder())

        with open(param_fname, 'w') as f:
            toml.dump({"Place": "Holder"}, f,
                      encoder=toml.TomlNumpyEncoder())


 #   {'False Positives': {'score': 6147, 'optimal': 0, 'type': 'int'},
 # 'False Negatives': {'score': 119, 'optimal': 0, 'type': 'int'},
 # 'People with >=3 FN': {'score': 0, 'optimal': 0, 'type': 'int'},
 # 'People with >=5 FP': {'score': 101, 'optimal': 0, 'type': 'int'},
 # 'Net profit': {'score': 2074, 'optimal': 100000000.0, 'type': 'float'}}


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