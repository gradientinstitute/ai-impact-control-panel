"""Python demo that does not invoke a frontend server."""
import click
from deva import elicit
import logging
from deva import fileio
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
@click.option('-b', '--bounds', default=False, is_flag=True)
def cli(scenario, method, bounds):
    logging.basicConfig(level=logging.INFO)

    candidates, scenario = fileio.load_scenario(scenario, bounds)
    eliciter = METHODS[method](candidates)
    display = interface.text

    while not eliciter.terminated:
        display(eliciter.query, scenario)

        i = None
        print(f'(Answer {eliciter.query[0].name} or {eliciter.query[1].name})')
        while i not in eliciter.query:
            i = input()
            if len(i) == 1:
                # Special shorthand?
                i = "System " + i
        eliciter.input(i)

    print('You have selected: ', eliciter.result.name)
    display(eliciter.result, scenario)
    input()
