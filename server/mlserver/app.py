from flask import Flask, session, jsonify, g
import toml
from deva.elicit import Toy, Eliciter
from deva.pareto import remove_non_pareto
from deva import fileio
import random
import string
import os
from dataclasses import dataclass


@dataclass
class ElicitState:
    """Perhaps the eliciter object needs to expose more state?"""
    eliciter: Eliciter
    choices: list
    stage: int


def random_key(n):
    return ''.join(random.choice(string.ascii_letters) for i in range(n))


# In the future the user might request a particular scenario
def load_models(scenario):
    # Expand into absolute path
    abs_path = os.path.join(fileio.repo_root(), "scenarios/"+scenario)

    input_files = fileio.get_all_files(abs_path)

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

    return models


app = Flask(__name__)
app.config['SECRET_KEY'] = random_key(12)

# the g application context didnt work - it has the lifetime of a request.
states = {}
models = None


@app.route('/choice')
def initial_view():
    global states, models

    if models is None:
        print("Initialising")
        models = load_models("example")

    if "ID" not in session:
        print("New user")
        session["ID"] = random_key(12)
        session.modified = True

    eliciter = Toy(models)
    (m1, m1perf), (m2, m2perf) = eliciter.prompt()

    # assume a page reload means they want to start again
    # potentially thread lock here
    states[session["ID"]] = ElicitState(
        eliciter=eliciter,
        choices=[[m1, m2]],
        stage=0,
    )

    # send the performance and choices
    m1perf["name"] = m1
    m2perf["name"] = m2
    return jsonify(model1=m1perf, model2=m2perf)


@app.route('/choice/<stage>/<x>')
def update(stage, x):
    global states, models
    if "ID" not in session:
        print("Invalid ID")
        return
    state = states[session["ID"]]

    if not state.eliciter.finished():
        stage = int(stage) - 1
        if stage < state.stage:
            print("Response from previous state.")
            return
        choice = state.choices[stage]
        if x == "1":
            select = choice[0]
        elif x == "2":
            select = choice[1]
        state.eliciter.user_input(select)

    if state.eliciter.finished():
        # Now we need some way of terminating?
        result_name, result = state.eliciter.final_output()
        result["name"] = result_name
        res = dict(model1=result, model2=result)
    else:
        (m1, m1perf), (m2, m2perf) = state.eliciter.prompt()
        state.stage += 1
        state.choices.append([m1, m2])
        m1perf["name"] = m1
        m2perf["name"] = m2
        res = dict(model1=m1perf, model2=m2perf)

    return jsonify(res)
