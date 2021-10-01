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
    'max_smooth': elicit.ActiveMaxSmooth,
    'max_prim': elicit.ActiveMaxPrimary,
}


@click.command()
@click.argument('scenario', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option('-m', '--method', default='max',
              type=click.Choice(METHODS, case_sensitive=False),
              help='interactive model selection method.')
@click.option('-b', '--bounds', default=False, is_flag=True,
              help='interactively choose acceptable performance bounds.')
@click.option('-f', '--nofilter', default=False, is_flag=True,
              help='do not apply Pareto efficient model filter.')
def cli(scenario, method, bounds, nofilter):
    logging.basicConfig(level=logging.INFO)

    candidates, scenario = fileio.load_scenario(scenario, bounds, not nofilter)

    eliciter = METHODS[method](candidates, scenario)
    display = interface.text
    metrics = scenario["metrics"]

    while not eliciter.terminated:
        display(eliciter.query, metrics)

        i = None
        print(f'(Answer {eliciter.query[0].name} or {eliciter.query[1].name})')
        while i not in eliciter.query:
            i = input()
            if len(i) == 1:
                # Special shorthand?
                i = "System " + i
        eliciter.input(i)

    print('You have selected: ', eliciter.result.name)
    display(eliciter.result, metrics)
    input()
