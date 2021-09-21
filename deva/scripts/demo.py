import click
import toml
from deva import elicit
import logging
from deva.pareto import remove_non_pareto
from deva.bounds import remove_unacceptable
from deva import fileio
from deva import halfspace
import matplotlib.pyplot as plt
from deva import interface

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

    # Filter efficient set
    models = remove_non_pareto(models)

    # [Optionally] allow the user to define acceptability bounds prior
    if bounds:
        models = remove_unacceptable(models)

    if len(models) == 0:
        print("There are no acceptable candidates.")
        return

    candidates, scenario = demux(models)

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


def demux(models):
    """Demux candidates from scenario metadata.
    If we are happy with this, it will be a future issue to represent the
    config in this format to begin with.
    """
    # TODO: change the way a scenario config is encoded
    scenario = {
        "False Positives": {
            "icon":"FP",
            "description": "legitimate transaction{s} per month",
            "more": "additional",
            "less": "fewer",
            "prefix": "",
            "suffix": "trans / month",
            "action": "falsely flag{s}",
            "higherIsBetter": False,
            "countable": "number",
        },
        "False Negatives": {
            "icon": "FN",
            "description": "fraudulent transaction{s} per month",
            "more": "additional",
            "less": "fewer",
            "prefix": "",
            "suffix": "trans / month",
            "action": "overlook{s}",
            "higherIsBetter": False,
            "countable": "number",
        },
        "People with >=3 FN": {
            "icon": "FNWO",
            "description": "customer{s} with 3 or more overlooked fraud transactions",
            "more": "additional",
            "less": "fewer",
            "prefix": "",
            "suffix": "person{s}",
            "action": "burden{s}",
            "higherIsBetter": False,
            "countable": "number",
        },
        "People with >=5 FP": {
            "icon": "FPWO",
            "description": "customer{s} with 5 or more false flags",
            "more": "additional",
            "less": "fewer",
            "prefix": "",
            "suffix": "person{s}",
            "action": "burden{s}",
            "higherIsBetter": False,
            "countable": "number",
        },
        "Net profit": {
            "icon": "profit",
            "description": "net profit",
            "more": "more",
            "less": "less",
            "prefix": "$",
            "suffix": "",
            "action": "make{s}",
            "higherIsBetter": True,
            "countable": "amount",
        }
    }

    processed = set()
    scores = {}
    for i, vals in enumerate(models.values()):
        name = "System " + chr(65 + i)  # TODO: don't always rename
        scores[name] = {}
        for u in vals:
            assert u in scenario
            # Auto insert min, max name, extract score
            score = vals[u]['score']
            scores[name][u] = score

            if u not in processed:
                processed.add(u)
                scenario[u]["max"] = score
                scenario[u]["min"] = score
                scenario[u]["name"] = u  # not needed here, but in frontend
            else:
                scenario[u]["max"] = max(scenario[u]["max"], score)
                scenario[u]["min"] = min(scenario[u]["min"], score)

    # Put into candidate format...
    candidates = [elicit.Candidate(k, v) for k, v in scores.items()]
    return candidates, scenario
