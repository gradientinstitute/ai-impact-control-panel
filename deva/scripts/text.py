import click
import toml
from deva.elicit import Toy, ActiveRanking
import logging
from deva.pareto import remove_non_pareto
from deva import fileio


METHODS = {
    'toy': Toy,
    'active': ActiveRanking
}


def pretty_print_performance(name, d):
    print(f'Model {name}:')
    for k in sorted(d.keys()):
        if d[k]["type"] == "int":
            print(f'\t{k}: {d[k]["score"]}')
        else:
            print(f'\t{k}: {d[k]["score"]:0.2f}')
    print('\n')


@click.command()
@click.argument('scenario', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.option('-m', '--method', default='active',
              type=click.Choice(['active', 'toy'], case_sensitive=False))
def cli(scenario, method):
    logging.basicConfig(level=logging.INFO)
    input_files = fileio.get_all_files(scenario)

    models = {}
    for name, fs in input_files.items():
        fname = fs['metrics']
        models[name] = toml.load(fname)

    models = remove_non_pareto(models)

    # Give all the models easy to remember names.... [optionally]
    tmp = {}
    for i, model in enumerate(models.values()):
        tmp["System " + chr(65+i)] = model
    models = tmp

    print(f'Starting elicitation using the {method} method.\n')
    eliciter = METHODS[method.lower()](models)
    while not eliciter.finished():
        (m1, m1perf), (m2, m2perf) = eliciter.prompt()
        print("Which model do you prefer:\n")
        pretty_print_performance(m1, m1perf)
        pretty_print_performance(m2, m2perf)
        print(f'(Answer {m1} or {m2})')
        print('> ', end='')
        i = input()
        choice = eliciter.user_input("System " + i)
        if choice is not None:
            print(f'You preferred model {choice}')
        else:
            print('Invalid selection, please try again.')
    result_name, result = eliciter.final_output()
    print('\n\nSelection complete.' +
          ' Based on your preferences you have selected:\n')
    pretty_print_performance(result_name, result)
