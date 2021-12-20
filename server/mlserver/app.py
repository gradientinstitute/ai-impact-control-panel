from flask import (Flask, session, jsonify as _jsonify,
                   abort, request, send_from_directory)

# from flask_caching import Cache
from deva import elicit, bounds, fileio
import numpy as np

import random
import string
import os.path


def round_floats(o):
    """Recursively round floats pre-json."""
    if isinstance(o, float):
        return round(o, 3)
    elif isinstance(o, dict):
        return {k: round_floats(v) for k, v in o.items()}
    elif isinstance(o, (list, tuple, np.ndarray)):
        return [round_floats(x) for x in o]
    return o


def jsonify(o):
    """Apply flask's jsonify with some float formatting."""
    return _jsonify(round_floats(o))


def random_key(n):
    """Make a random string of n characters."""
    return ''.join(random.choice(string.ascii_letters) for i in range(n))


# Set up the flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = random_key(16)

# TODO: proper cache / serialisation
eliciters = {"toy": elicit.Toy, "activeranking": elicit.ActiveRanking,
             "activemax": elicit.ActiveMax,
             "activemaxsmooth": elicit.ActiveMaxSmooth,
             "activemaxprimary": elicit.ActiveMaxPrimary,
             "myeliciter": elicit.MyEliciter}

eliciters_descriptions = {k: v.description() for k, v in eliciters.items()}

bounders = {}
scenarios = {}
ranges = {}
baselines = {}


def calc_ranges(candidates, spec):
    keys = spec['metrics'].keys()
    points = [c.attributes for c in candidates]
    collated = {k: [p[k] for p in points] for k in keys}
    return points, collated


@app.route('/')
def check_status():
    return "Deva backend server status OK"


@app.route('/scenarios')
def get_scenarios():
    data = fileio.list_scenarios()
    return jsonify(data)


def _scenario(name="jobs"):
    global scenarios

    if name not in scenarios:
        data = fileio.load_scenario(name)

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


@app.route('/<scenario>/bounds/init', methods=['PUT'])
def init_bounds(scenario):
    global bounders

    if "BOUND_ID" in session:
        print("Reset session")
    else:
        print("Creating new session key")
        while (new_id := random_key(16)) in bounders:
            continue
        session["BOUND_ID"] = new_id
        session.modified = True

    ident = session["BOUND_ID"]

    candidates, meta = _scenario(scenario)
    baseline = meta["baseline"]
    metrics = meta["metrics"]
    attribs, table, sign = bounds.tabulate(candidates, metrics)
    ref = [baseline[a] for a in attribs]
    bounders[ident] = bounds.TestSampler(ref, table, sign, attribs, steps=15)
    return ""


@app.route('/<scenario>/bounds/choice', methods=['GET', 'PUT'])
def get_bounds_choice(scenario):
    global bounders

    if "BOUND_ID" not in session:
        print("Session not initialised!")
        abort(400)  # Not initialised

    sampler = bounders[session["BOUND_ID"]]

    # if we received a choice, process it
    if request.method == "PUT":
        print("PUT METHOD")
        data = request.get_json(force=True)
        print("Data is:", data)
        x = data["first"]
        y = data["second"]
        print(x, y)
        options = [sampler.query.name, "Baseline"]
        valid = (x in options) & (y in options)

        # Only pass valid choices on to the eliciter
        if (not sampler.terminated and valid):
            sampler.observe(x == sampler.query.name)
        else:
            print("Ignoring input")

    if sampler.terminated:
        # TODO consider return options.
        # For now, making it closely resemble the eliciter's returns
        res = {
                "hyperplane": {
                    "origin": sampler.baseline.attributes,
                    "normal": dict(zip(sampler.attribs, sampler.w)),
                }
        }
    else:
        # eliciter has not terminated - extract the next choice
        assert isinstance(sampler.query, elicit.Candidate)
        assert isinstance(sampler.baseline, elicit.Candidate)
        res = {
            "left": {
                "name": sampler.query.name,
                "values": sampler.query.attributes,
                },
            "right": {
                "name": "Baseline",
                "values": sampler.baseline.attributes,
                }
        }

    return jsonify(res)


@app.route('/algorithms')
def get_algorithm():
    """
      Return which algorithms are available.
    """
    return jsonify(eliciters_descriptions)


@app.route('/<scenario>/init/<algo>')
def init_session(scenario, algo):
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
    # TODO: user choice
    eliciter = eliciters[algo](candidates, spec)

    eliciters[session["ID"]] = eliciter
    ranges[session["ID"]] = calc_ranges(candidates, spec)

    # send the metadata for the scenario
    return spec


@app.route('/<scenario>/ranges', methods=['GET'])
def get_ranges(scenario):
    global ranges

    # if "ID" not in session:
    #     print("Session not initialised!")
    #     abort(400)  # Not initialised

    candidates, spec = _scenario(scenario)
    points, _collated = calc_ranges(candidates, spec)
    return jsonify(points)


@app.route('/<scenario>/baseline', methods=['GET'])
def get_baseline(scenario):
    global baselines

    # We can just load from disk every time if we configure caching
    if scenario not in baselines:
        baselines[scenario] = fileio.load_baseline(scenario)

    return jsonify(baselines[scenario])


@app.route('/<scenario>/constraints', methods=['PUT'])
def apply_constraints(scenario):
    data = request.get_json(force=True)
    print(data)
    return "OK"


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
