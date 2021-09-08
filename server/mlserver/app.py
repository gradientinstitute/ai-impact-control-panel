from flask import Flask, session, jsonify
import toml
from deva.elicit import Toy
from deva.pareto import remove_non_pareto
from deva import fileio
import random
import string
import os


def random_key(n):
    """Make a random string of n characters."""
    return ''.join(random.choice(string.ascii_letters) for i in range(n))


# In the future the user might request a particular scenario
def load_models(scenario):
    """Load and shortlist a scenario's pareto efficient models."""
    abs_path = os.path.join(fileio.repo_root(), "scenarios/" + scenario)
    input_files = fileio.get_all_files(abs_path)

    models = {}
    for name, fs in input_files.items():
        fname = fs['metrics']
        models[name] = toml.load(fname)

    models = remove_non_pareto(models)

    # Give all the models easy to remember names
    renamed = {}
    for i, model in enumerate(models.values()):
        renamed["System " + chr(65+i)] = model

    return renamed


# Set up the flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = random_key(12)

# TODO: app-wide persistent server-side session data
# flask g application context didnt work - it has the lifetime of a request.
session_eliciters = {}
models = None


@app.route('/choice')
def initial_view():
    global session_eliciters, models

    if models is None:
        print("Initialising")
        models = load_models("example")

    if "ID" not in session:
        print("New user")
        session["ID"] = random_key(12)
        session.modified = True

    eliciter = Toy(models)
    (m1, m1perf), (m2, m2perf) = eliciter.prompt()
    eliciter.choice = (m1, m2)  # will change the eliciter API to remember this

    # assume a page reload means they want to start again
    session_eliciters[session["ID"]] = eliciter

    # send the performance and choices to the frontend
    m1perf["name"] = m1
    m2perf["name"] = m2
    return jsonify(model1=m1perf, model2=m2perf)


@app.route('/choice/<stage>/<x>')  # TODO: replace stage with tuple as below
def update(stage, x):
    global session_eliciters, models
    if "ID" not in session:
        return jsonify("Invalid")

    eliciter = session_eliciters[session["ID"]]

    if not eliciter.finished():
        # TODO: front-end needs a termination signal
        # Only accept a choice if the eliciter has not terminated

        # TODO: it would be unambiguous if front-end responded with name of
        # preferred choice and non-preferred choice as a signal
        if x == "1":
            select = eliciter.choice[0]
        elif x == "2":
            select = eliciter.choice[1]
        eliciter.user_input(select)

    if eliciter.finished():
        result_name, result = eliciter.final_output()
        result["name"] = result_name

        # TODO: front-end needs a termination signal
        # For now just respond with two copies of the final model
        res = dict(model1=result, model2=result)
    else:
        # eliciter has not terminated - extract the next choice
        (m1, m1perf), (m2, m2perf) = eliciter.prompt()
        eliciter.choice = (m1, m2)
        m1perf["name"] = m1
        m2perf["name"] = m2
        res = dict(model1=m1perf, model2=m2perf)

    return jsonify(res)
