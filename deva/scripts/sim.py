import click
from deva.config import parse_config
from deva.datasim import simulate
import logging
from logging import info
import os


@click.argument('simfile', type=click.Path(
    exists=True, file_okay=True, dir_okay=False, resolve_path=True))
@click.command()
def cli(simfile):
    logging.basicConfig(level=logging.INFO)
    data_folder = os.path.dirname(simfile)
    with open(simfile, 'r') as f:
        sim_cfg = parse_config(f)
    sim_name = os.path.splitext(os.path.basename(simfile))[-2]
    X_train, X_test = simulate(sim_cfg)
    fname_train = f'{sim_name}_train.csv'
    fname_test = f'{sim_name}_test.csv'
    X_train.to_csv(os.path.join(data_folder, fname_train))
    info(f"saved {fname_train}")
    X_test.to_csv(os.path.join(data_folder, fname_test))
    info(f"saved {fname_test}")
