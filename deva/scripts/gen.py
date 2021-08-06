import click
from deva.config import parse_config
from deva.model import build_model
import os
from deva.datasim import simulate
import logging
from logging import info
import pandas as pd
from joblib import dump


@click.group()
@click.option('--data-folder', default='data')
@click.option('--sim', type=click.File('r'), required=True)
@click.pass_context
def cli(ctx, data_folder, sim):
    ctx.ensure_object(dict)
    logging.basicConfig(level=logging.INFO)
    data_folder = os.path.join(os.getcwd(), data_folder)
    ctx.obj['data_folder'] = data_folder
    cfg = parse_config(sim)
    sim_name = os.path.splitext(sim.name)[0]
    ctx.obj['sim_name'] = sim_name
    ctx.obj['sim_cfg'] = cfg


@cli.command()
@click.pass_context
def data(ctx):
    data_folder = ctx.obj['data_folder']
    cfg = ctx.obj['sim_cfg']
    sim_name = ctx.obj['sim_name']

    X_train, X_test = simulate(cfg)
    fname_train = f'{sim_name}_sim_train.csv'
    fname_test = f'{sim_name}_sim_test.csv'
    X_train.to_csv(os.path.join(data_folder, fname_train))
    info(f"saved {fname_train}")
    X_test.to_csv(os.path.join(data_folder, fname_test))
    info(f"saved {fname_test}")


@cli.command()
@click.argument('model', type=click.File('r'))
@click.pass_context
def model(ctx, model):
    sim_name = ctx.obj['sim_name']

    model_name = os.path.splitext(model.name)[0]
    cfg = parse_config(model)
    data_folder = ctx.obj['data_folder']
    fname_train = os.path.join(data_folder,
                               f'{sim_name}_sim_train.csv')
    fname_test = os.path.join(data_folder,
                              f'{sim_name}_sim_test.csv')

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
    y_scored, mdl = build_model(X_train, y_train, t_train,
                                X_test, y_test, t_test, cfg)

    out_fname = os.path.join(
            data_folder, f'{sim_name}_sim_scoredby_{model_name}.csv')
    y_scored.to_csv(out_fname)

    # Write the model to disk
    model_fname = os.path.join(
            data_folder, f'{sim_name}_sim_trained_{model_name}.joblib')
    dump(mdl, model_fname)
