import click
from deva.config import parse_config
import os
from deva.datasim import simulate
import logging
from logging import info

@click.command()
@click.argument('configfile', type=click.File('r'))
@click.option('-o', '--output-folder', default='data')
def cli(configfile, output_folder):
    logging.basicConfig(level=logging.INFO)
    sim_name = os.path.splitext(configfile.name)[0]
    cfg = parse_config(configfile)
    d = simulate(cfg)
    fname_prefix = os.path.join(os.getcwd(), output_folder)

    for t, d_t in d.items():
        for lbl, d_tt in d_t.items():
            fname = f'{sim_name}_{lbl}_{t}.csv'
            info(f"saving {fname}")
            d_tt.to_csv(os.path.join(fname_prefix, fname))

