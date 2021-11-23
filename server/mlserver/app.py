from flask import Flask, session, jsonify, abort, request, send_from_directory
# from flask_caching import Cache
from deva import elicit
from deva import fileio
import random
import string
import os.path


def random_key(n):
    """Make a random string of n characters."""
    return ''.join(random.choice(string.ascii_letters) for i in range(n))


# Set up the flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = random_key(16)

# todo: find some sort of persistent cache
eliciters = {}
scenarios = {}
ranges = {}


def calc_ranges(candidates, spec):
    keys = spec['metrics'].keys()
    points = [c.attributes for c in candidates]
    collated = {k: [p[k] for p in points] for k in keys}
    return points, collated


@app.route('/scenarios')
def get_scenarios():
    data = fileio.list_scenarios()
    return jsonify(data)


def _scenario(name="jobs"):
    global scenarios

    if name not in scenarios:
        data = fileio.load_scenario(name, False)

        # Massage the metadata
        models, spec = data
        metrics = spec["metrics"]
        for attr in metrics:
            for key in metrics[attr]:
                # get rid of my plural adjustments for now
                if isinstance(metrics[attr][key], str):
                    metrics[attr][key] = metrics[attr][key].format(s="s")

        for m in models:
            # make html-friendly uuid
            m.name = m.name.replace(" ", "_")

        scenarios[name] = (models, spec)

    return scenarios[name]


@app.route('/<scenario>/images/<path:name>')
def send_image(scenario, name):
    print("trying to get image")
    scenario_path = os.path.join(fileio.repo_root(),
                                 f'scenarios/{scenario}/images')
    return send_from_directory(scenario_path, name)


@app.route('/<scenario>/metadata')
def init_session(scenario):
    global eliciters

    if "ID" in session:
        print("Reset session")
    else:
        print("New session")
        while (new_id := random_key(16)) in eliciters:
            continue
        session["ID"] = new_id
        session.modified = True

    # assume that a reload means user wants a restart
    print("Init new session for ", session["ID"])
    candidates, spec = _scenario(scenario)
    eliciter = elicit.ActiveMaxSmooth(candidates, spec)  # TODO: user choice?
    # eliciter = elicit.ActiveMax(candidates, spec)
    eliciters[session["ID"]] = eliciter
    ranges[session["ID"]] = calc_ranges(candidates, spec)

    # send the metadata for the scenario
    return spec


@app.route('/<scenario>/ranges', methods=['GET'])
def get_ranges(scenario):
    global ranges

    if "ID" not in session:
        print("Session not initialised!")
        abort(400)  # Not initialised

    candidates, spec = _scenario(scenario)
    points, _collated = calc_ranges(candidates, spec)
    return jsonify(points)


@app.route('/<scenario>/choice', methods=['GET', 'PUT'])
def get_choice(scenario):
    global eliciters

    if "ID" not in session:
        print("Session not initialised!")
        abort(400)  # Not initialised

    eliciter = eliciters[session["ID"]]

    # if we got a choice, process it
    if request.method == "PUT":
        data = request.get_json(force=True)
        x = data["first"]
        y = data["second"]
        # Only pass valid choices on to the eliciter
        if not eliciter.terminated:
            choice = eliciter.query
            if (x in choice) and (y in choice) and (x != y):
                eliciter.input(x)

    # now give some new choices
    if eliciter.terminated:
        # terminate by sending a single model
        result = eliciter.result
        res = {result.name: {
                'attr': result.attributes,
                'spec': result.spec_name
        }}
    else:
        # eliciter has not terminated - extract the next choice
        assert isinstance(eliciter.query, elicit.Pair)
        m1, m2 = eliciter.query
        res = {
                "left": {
                    "name": m1.name,
                    "values": m1.attributes
                    },
                "right": {
                    "name": m2.name,
                    "values": m2.attributes
                    }
            }
    return jsonify(res)
