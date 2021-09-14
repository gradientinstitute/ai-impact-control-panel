import click
import toml
from deva import elicit
import logging
from deva.pareto import remove_non_pareto
from deva import fileio


def pretty_print_performance(name, d):
    print(f'{name}:')
    for k in sorted(d.keys()):
        if d[k]["type"] == "int":
            print(f'\t{k}: {d[k]["score"]}')
        else:
            print(f'\t{k}: {d[k]["score"]:0.2f}')
    print('\n')


@click.command()
@click.argument('scenario', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, resolve_path=True))
def cli(scenario):
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

    eliciter = elicit.Toy(models)
    while not eliciter.terminated:
        assert isinstance(eliciter.query, elicit.Pairwise)
        m1, m2 = eliciter.query
        pretty_print_performance(m1, models[m1])
        pretty_print_performance(m2, models[m2])
        print("Which model do you prefer:\n")

        i = ""
        while i not in eliciter.query:
            print(f'(Answer {m1.split()[-1]} or {m2.split()[-1]})')
            print('> ', end='')
            i = "System " + input()

        eliciter.update(i)

    print('\n\nSelection complete.' +
          ' Based on your preferences you have selected:\n')
    pretty_print_performance(eliciter.result, models[eliciter.result])
