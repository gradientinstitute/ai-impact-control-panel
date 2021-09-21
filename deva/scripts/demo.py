import click
import toml
from deva import elicit
import logging
from deva.pareto import remove_non_pareto
from deva.bounds import remove_unacceptable
from deva import fileio
import matplotlib.pyplot as plt
from deva import interface
import os.path


# Elicitation methods
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

    # Load all scenario files
    input_files = fileio.get_all_files(scenario)
    models = {}
    for name, fs in input_files.items():
        fname = fs['metrics']
        models[name] = toml.load(fname)

    scenario = toml.load(os.path.join(scenario, "metadata.toml"))

    # Filter efficient set
    models = remove_non_pareto(models)

    # [Optionally] allow the user to define acceptability bounds prior
    if bounds:
        models = remove_unacceptable(models)

    if len(models) == 0:
        print("There are no acceptable candidates.")
        return

    candidates = get_candidates(models)

    # Auto-insert the set-min and set-max into the scenario
    for u in scenario:
        scenario[u]["max"] = max(c[u] for c in candidates)
        scenario[u]["min"] = min(c[u] for c in candidates)

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


def get_candidates(models):
    """
    Convert the TOML-loaded dictionaries into candidate objects.
    TODO: change format upstream to remove metadata from model score files.
    """
    candidates = []

    for perf in models.values():
        # TODO: retain "special" names of reference models.
        name = "System " + chr(65 + len(candidates))
        scores = {k: v['score'] for k, v in perf.items()}
        candidates.append(elicit.Candidate(name, scores))

    return candidates
