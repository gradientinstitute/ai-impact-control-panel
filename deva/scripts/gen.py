import click
from deva.config import parse_config
from deva.model import iter_models
import os
import logging
from logging import info
import pandas as pd
from joblib import dump
import toml


@click.argument('scenario', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.command()
def cli(scenario):
    logging.basicConfig(level=logging.INFO)
    data_folder = os.path.join(os.getcwd(), 'data')
    model_folder = os.path.join(scenario, 'models')
    os.makedirs(model_folder, exist_ok=True)
    model_cfg_fname = os.path.join(scenario, 'model.toml')
    with open(model_cfg_fname, 'r') as f:
        cfg = parse_config(f, build_tuple=False)
    data_name = cfg['data_simulation']
    fname_train = os.path.join(data_folder, f'{data_name}_train.csv')
    fname_test = os.path.join(data_folder, f'{data_name}_test.csv')

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
