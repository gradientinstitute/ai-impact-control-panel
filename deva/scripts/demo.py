"""Python demo that does not invoke a frontend server."""
import click
from deva import elicit
import logging
from deva import fileio
import matplotlib.pyplot as plt
from deva import interface

METHODS = {
    'toy': elicit.Toy,
    'rank': elicit.ActiveRanking,
    'max': elicit.ActiveMax,
}


@click.command()
@click.argument('scenario', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option('-m', '--method', default='max',
              type=click.Choice(['max', 'rank', 'toy'], case_sensitive=False))
@click.option('-g', '--gui', default=False, is_flag=True)
@click.option('-b', '--bounds', default=False, is_flag=True)
def cli(scenario, method, bounds, gui):
    logging.basicConfig(level=logging.INFO)

    candidates, scenario = fileio.load_scenario(scenario, bounds)
    eliciter = METHODS[method](candidates)
    show = interface.text

    if gui:
        show = interface.mpl
        plt.figure(figsize=(10, 6), dpi=120)

    # should the loop be event driven or a loop with blocking calls?
    while not eliciter.terminated:
        show(eliciter.query, scenario)

        i = None
        print(f'(Answer {eliciter.query[0].name} or {eliciter.query[1].name})')
        while i not in eliciter.query:
            i = input()
            if len(i) == 1:
                i = "System " + i
        eliciter.input(i)

    print('You have selected: ', eliciter.result.name)
    show(eliciter.result, scenario)
    input()
