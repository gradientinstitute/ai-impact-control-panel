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
@click.argument('configfile', type=click.File('r'))
@click.option('-f', '--data-folder', default='data')
@click.pass_context
def cli(ctx, configfile, data_folder):
    ctx.ensure_object(dict)
    logging.basicConfig(level=logging.INFO)
    sim_name = os.path.splitext(configfile.name)[0]
    data_folder = os.path.join(os.getcwd(), data_folder)

    cfg = parse_config(configfile)
    ctx.obj['cfg'] = cfg
    ctx.obj['sim_name'] = sim_name
    ctx.obj['data_folder'] = data_folder


@cli.command()
@click.pass_context
def data(ctx):
    cfg = ctx.obj['cfg']
    sim_name = ctx.obj['sim_name']
    data_folder = ctx.obj['data_folder']

    d = simulate(cfg)

    for t, d_t in d.items():
        for lbl, d_tt in d_t.items():
            fname = f'{sim_name}_{lbl}_{t}.csv'
            info(f"saving {fname}")
            d_tt.to_csv(os.path.join(data_folder, fname))

@cli.command()
@click.pass_context
def model(ctx):

    cfg = ctx.obj['cfg']
    data_folder = ctx.obj['data_folder']
    sim_name = ctx.obj['sim_name']
    fname_train = os.path.join(data_folder, f'{sim_name}_transaction_train.csv')
    fname_test = os.path.join(data_folder, f'{sim_name}_transaction_test.csv')

    # Load train data
    df = pd.read_csv(fname_train)
    df.set_index('ID', inplace=True)
    X_train = df.drop(['trans_time', 'response'], axis=1)
    y_train = df.response
    t_train = df.trans_time

    # Load validation data
    df_val = pd.read_csv(fname_test)
    df_val.set_index("ID", inplace=True)
    X_test = df_val.drop(["trans_time", "response"], axis=1)
    y_test = df_val.response
    t_test = df_val.trans_time
    mdl = build_model(X_train, y_train, t_train, X_test, y_test, t_test, cfg)

    #Write the model to disk
    model_fname = os.path.join(data_folder, f'{sim_name}_model.joblib')
    dump(mdl, model_fname)
