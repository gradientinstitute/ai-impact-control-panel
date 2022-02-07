"""Python demo that does not invoke a frontend server."""
import click
from deva import elicit
import logging
from deva import fileio
from deva import interface


@click.command()
@click.argument("scenario", type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option("-m", "--method", default="max",
              type=click.Choice(elicit.algorithms, case_sensitive=False),
              help="interactive model selection method.")
@click.option("-b", "--bounds", default=False, is_flag=True,
              help="interactively choose acceptable performance bounds.")
@click.option("-f", "--nofilter", default=False, is_flag=True,
              help="do not apply Pareto efficient model filter.")
def cli(scenario, method, bounds, nofilter):
    """Run a (server-free) demo of the eliciter framework."""
    logging.basicConfig(level=logging.INFO)

    candidates, scenario = fileio.load_scenario(scenario, bounds, not nofilter)
    display = interface.text
    metrics = scenario["metrics"]

    if len(candidates) == 1:
        result = candidates[0]
        print("Remaining model: ", result.name)
        display(result, metrics)
        input()
        return

    eliciter = elicit.algorithms[method](candidates, scenario)
    while not eliciter.terminated():
        query = eliciter.query()
        display(query, metrics)

        i = None
        print(f"(Answer {query[0].name} or {query[1].name})")
        while i not in query:
            i = input()
            if len(i) == 1:
                # Special shorthand?
                i = "System " + i
        eliciter.put(i)

    print("You have selected: ", eliciter.result().name)
    display(eliciter.result(), metrics)
    input()
