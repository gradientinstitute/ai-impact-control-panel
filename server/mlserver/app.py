"""Flask backend elicitation server for AI Impact Control Panel."""

import os
import os.path
from util import jsonify, random_key

import redis
import toml
from flask import Flask, session, abort, request, send_from_directory
from fpdf import FPDF

from deva import elicit, bounds, fileio, logger
from deva.db import RedisDB, DevDB

import pickle

# Set up the flask app
app = Flask(__name__)
app.config.from_envvar('DEVA_MLSERVER_CONFIG')

# Secret key for signing session cookies
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")
app.config['SECRET_KEY'] = SECRET_KEY

# Database for production is redis, is a dict for development
if app.config['ENV'] == 'production':
    print("Using production database (redis)")
    r = redis.Redis(host=app.config['REDIS_SERVER'],
                    port=app.config['REDIS_PORT'],
                    db=0,
                    socket_connect_timeout=2)
    db = RedisDB(r, session)
else:
    print("Using development database (thread local object)")
    db = DevDB(session)

# TODO: proper cache / serialisation
eliciters_descriptions = {k: v.description()
                          for k, v in elicit.algorithms.items()}


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
    if 'id' not in session:
        session['id'] = random_key(16)
    data = fileio.list_scenarios()
    return jsonify(data)


def _scenario(name="jobs"):

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

    result = (models, spec)

    return result


@app.route('/<scenario>/images/<path:name>')
def send_image(scenario, name):
    scenario_path = os.path.join(fileio.repo_root(),
                                 f'scenarios/{scenario}/images')
    return send_from_directory(scenario_path, name)


@app.route('/log/<path:name>')
def send_log(name):
    scenario_path = 'logs'
    return send_from_directory(scenario_path, name)


@app.route('/<scenario>/bounds/init', methods=['PUT'])
def init_bounds(scenario):
    if 'id' not in session:
        session['id'] = random_key(16)
    candidates, meta = _scenario(scenario)
    baseline = meta["baseline"]
    metrics = meta["metrics"]
    attribs, table = bounds.tabulate(candidates, metrics)
    ref = [baseline[a] for a in attribs]
    db.bounder = bounds.PlaneSampler(ref, table, attribs, steps=30)
    return ""


@app.route('/<scenario>/bounds/choice', methods=['GET', 'PUT'])
def get_bounds_choice(scenario):

    if db.bounder is None:
        print("Session not initialised!")
        abort(400)  # Not initialised
    sampler = db.bounder

    # if we received a choice, process it
    if request.method == "PUT":
        data = request.get_json(force=True)
        x = data["first"]
        y = data["second"]
        options = [sampler.query.name, "Baseline"]
        valid = (x in options) & (y in options)

        # Only pass valid choices on to the eliciter
        if (not sampler.terminated and valid):
            sampler.observe(x == sampler.query.name)
        else:
            print("Ignoring input")

    if sampler.terminated:
        model_id = random_key(16)
        path = "models/" + model_id + ".toml"
        if not os.path.exists('models'):
            os.mkdir('models')
        pickle.dump(sampler, open(path, "wb"))
        res = {"model_ID": path}

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

    # Update database state
    db.bounder = sampler

    return jsonify(res)


@app.route('/algorithms')
def get_algorithm():
    """
      Return which algorithms are available.
    """
    return jsonify(eliciters_descriptions)


@app.route('/<scenario>/init/<algo>/<name>')
def init_session(scenario, algo, name):
    if 'id' not in session:
        session['id'] = random_key(16)
    # assume that a reload means user wants a restart
    print("Init new session for user")
    candidates, spec = _scenario(scenario)
    eliciter = elicit.algorithms[algo](candidates, spec)
    log = logger.Logger(scenario, algo, name)
    db.eliciter = eliciter
    db.logger = log
    # send the metadata for the scenario
    return spec


@app.route('/<scenario>/ranges', methods=['GET'])
def get_ranges(scenario):

    candidates, spec = _scenario(scenario)
    points, _collated = calc_ranges(candidates, spec)
    return jsonify(points)


@app.route('/<scenario>/baseline', methods=['GET'])
def get_baseline(scenario):
    result = fileio.load_baseline(scenario)
    return jsonify(result)


@app.route('/<scenario>/constraints', methods=['PUT'])
def apply_constraints(scenario):
    # _ = request.get_json(force=True)
    return "OK"


@app.route('/Enautilus/zpoints')
def get_z():
    eliciter = db.eliciter
    if db.eliciter is None:
        print("Session not initialised!")
        abort(400)  # Not initialised

    # log = loggers[session["ID"]]
    return jsonify(eliciter.get_z_points())


@app.route('/<scenario>/choice', methods=['GET', 'PUT'])
def get_choice(scenario):

    if db.eliciter is None:
        print("Session not initialised!")
        abort(400)  # Not initialised

    eliciter = db.eliciter
    log = db.logger

    # if we got a choice, process it
    if request.method == "PUT":
        print("PUT")
        data = request.get_json(force=True)
        log.add_choice([data])
        x = data["first"]

        # Only pass valid choices on to the eliciter
        if not eliciter.terminated:
            eliciter.input(x)
    if eliciter.terminated:
        result = eliciter.result
        res = {result.name: {
                'attr': result.attributes,
                'spec': result.spec_name
        }}
        log.add_result(res)
        data = log.get_log()
        if not os.path.exists('logs'):
            os.mkdir('logs')
        output_file_name = f"logs/{session['id']}.toml"
        with open(output_file_name, "w") as toml_file:
            toml.dump(data, toml_file)
        pdf = FPDF()
        # Add a page
        pdf.add_page()
        # set style and size of font
        # that you want in the pdf
        pdf.set_font("Arial", size=15)
        f = open(output_file_name, "r")
        for lines in f:
            pdf.cell(200, 10, txt=lines, ln=1, align='C')
        pdf.output(f"logs/{str(session['id'])}.pdf")
    else:
        res = []
        for option in eliciter.query:
            res.append({'name': option.name, 'values': option.attributes})
    db.eliciter = eliciter
    db.logger = log
    return jsonify(res)
