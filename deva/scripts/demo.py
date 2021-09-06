import click
import toml
from deva.elicit import Toy
from deva import fileio
import logging
from deva.pareto import remove_non_pareto
import matplotlib.pyplot as plt
from deva.vis import comparison


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
def cli(scenario):
    logging.basicConfig(level=logging.INFO)
    input_files = fileio.get_all_files(scenario)

    models = {}
    for name, fs in input_files.items():
        fname = fs['metrics']
        models[name] = toml.load(fname)

    models = remove_non_pareto(models)

    # icon_key = ["profit", "FNWO", "FPWO", "FP", "FN", "CORRECT", "INCORRECT"]
    remap = {
        'False Positives': 'FP',
        'False Negatives': 'FN',
        'People with >=3 FN': 'FNWO',
        'People with >=5 FP': 'FPWO',
        'Net profit': 'profit'
    }
    maxima = {}

    # Give all the models easy to remember names.... [optionally]
    tmp = {}
    for i, model in enumerate(models.values()):
        tmp["System " + chr(65+i)] = model
    models = tmp

    # compute set-wide maxima  - assuming positive for demo purposes
    for model in models.values():
        for k, v in model.items():
            a = remap[k]
            maxima[a] = max(maxima.get(a, 0), v["score"])

    eliciter = Toy(models)
    plt.figure(figsize=(10, 8))
    plt.ion()

    while not eliciter.finished():
        (m1, m1perf), (m2, m2perf) = eliciter.prompt()

        # patch into the visualisation
        sys1 = {remap[k]: m1perf[k]["score"] for k in remap}
        sys2 = {remap[k]: m2perf[k]["score"] for k in remap}
        sys1["name"] = m1
        sys2["name"] = m2

        plt.clf()
        # plt.gcf().set_size_inches(10, 8)
        comparison(sys1, sys2, scale=maxima)  # remap=remap
        plt.draw()
        plt.show(block=False)
        # plt.pause(0.01)

        print("Which model do you prefer:\n")
        m1 = m1.split()[-1]  # just A or B
        m2 = m2.split()[-1]
        print(f'(Answer {m1} or {m2})')
        print('> ', end='')
        i = input()
        choice = eliciter.user_input("System " + i)
        if choice is not None:
            print(f'You preferred model {choice}')
        else:
            print('Invalid selection, please try again.')
    result_name, result = eliciter.final_output()
    print('\n\nYou have selected:', result_name)
    # pretty_print_performance(result_name, result)

    plt.clf()
    sys1 = {remap[k]: result[k]["score"] for k in remap}
    sys1["name"] = result_name
    comparison(sys1, None, scale=maxima)  # remap=remap
    plt.draw()
    plt.pause(0.1)
    input()
