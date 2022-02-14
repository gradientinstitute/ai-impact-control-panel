"""Flask backend elicitation server for AI Impact Control Panel."""

import os
import os.path
from util import jsonify, random_key

import redis
import toml
from flask import Flask, session, abort, request, send_from_directory
from fpdf import FPDF

from deva import elicit, bounds, fileio, logger, compareBase
from deva.db import RedisDB, DevDB


import pickle

# Set up the flask app
app = Flask(__name__)
app.config.from_envvar("DEVA_MLSERVER_CONFIG")

# Secret key for signing session cookies
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")
app.config["SECRET_KEY"] = SECRET_KEY

# Database for production is redis, is a dict for development
if app.config["ENV"] == "production":
    print("Using production database (redis)")
    r = redis.Redis(host=app.config["REDIS_SERVER"],
                    port=app.config["REDIS_PORT"],
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
    """Extract a list of attributes and their ranges."""
    keys = spec["metrics"].keys()
    points = [c.attributes for c in candidates]
    collated = {k: [p[k] for p in points] for k in keys}
    return points, collated


@app.route("/")
def check_status():
    """Confirm API status."""
    return "Deva backend server status OK"


@app.route("/scenarios")
def get_scenarios():
    """List the available API scenarios."""
    if "id" not in session:
        session["id"] = random_key(16)
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


@app.route("/<scenario>/images/<path:name>")
def send_image(scenario, name):
    """Send target image to client."""
    scenario_path = os.path.join(fileio.repo_root(),
                                 f"scenarios/{scenario}/images")
    return send_from_directory(scenario_path, name)


@app.route("/log/<path:name>")
def send_log(name):
    """Send the session logs to the client."""
    scenario_path = "logs"
    return send_from_directory(scenario_path, name)


@app.route("/<scenario>/bounds/save", methods=["PUT"])
def save_bound(scenario):
    """Save the bounds configurations to the server."""
    file_name = f"scenarios/{scenario}/bounds.toml"
    path = os.path.join(fileio.repo_root(), file_name)
    with open(path, "w+") as toml_file:
        toml.dump(request.json, toml_file)

    # return report text
    bounds = toml.load(path)
    meta = _scenario(scenario)[1]
    baselines = meta["baseline"]
    report = compareBase.compare(meta, baselines, bounds)
    return report


@app.route("/<scenario>/bounds/init", methods=["PUT"])
def init_bounds(scenario):
    """Initialise a bounds elicitation session."""
    if "id" not in session:
        session["id"] = random_key(16)
    candidates, meta = _scenario(scenario)
    baseline = meta["baseline"]
    metrics = meta["metrics"]
    attribs, table = bounds.tabulate(candidates, metrics)
    ref = [baseline["industry_average"][a] for a in attribs]
    db.bounder = bounds.PlaneSampler(ref, table, attribs, steps=30)
    return ""


@app.route("/<scenario>/bounds/choice", methods=["GET", "PUT"])
def get_bounds_choice(scenario):
    """Accept the user's choice for a bounds elicitation session."""
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
        if (not sampler.terminated() and valid):
            sampler.put(x == sampler.query.name)
        else:
            print("Ignoring input")

    if sampler.terminated():
        model_id = random_key(16)
        path = "models/" + model_id + ".toml"
        if not os.path.exists("models"):
            os.mkdir("models")
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
            },
        }

    # Update database state
    db.bounder = sampler

    return jsonify(res)


@app.route("/algorithms")
def get_algorithm():
    """Return names and descriptions of available eliciter algorithms."""
    return jsonify(eliciters_descriptions)


@app.route("/<scenario>/init/<algo>/<name>")
def init_session(scenario, algo, name):
    """Initialise a preference elicitation session."""
    if "id" not in session:
        session["id"] = random_key(16)
    # assume that a reload means user wants a restart
    print("Init new session for user")
    candidates, spec = _scenario(scenario)
    eliciter = elicit.algorithms[algo](candidates, spec)
    log = logger.Logger(scenario, algo, name)
    db.eliciter = eliciter
    db.logger = log
    # send the metadata for the scenario
    return spec


@app.route("/deployment/new", methods=["PUT"])
def make_new_deployment_session():
    """Initialise an eliciter with a particular algorithm and scenario."""
    # get info about setup from the frontend
    data = request.get_json(force=True)
    scenario = data["scenario"]
    algo = data["algorithm"]
    name = data["name"]

    if "id" not in session:
        session["id"] = random_key(16)
    # assume that a reload means user wants a restart
    print("Init new session for user")
    candidates, spec = _scenario(scenario)
    eliciter = elicit.algorithms[algo](candidates, spec)
    log = logger.Logger(scenario, algo, name)
    db.eliciter = eliciter
    db.logger = log
    # send the metadata for the scenario
    return spec


# TODO this could replace some of the other calls
@app.route("/<scenario>/all")
def get_all(scenario):
    """Get all the relevent info about a scenario."""
    candidates, spec = _scenario(scenario)
    points, _ = calc_ranges(candidates, spec)
    baselines = []
    # baselines = fileio.load_baseline(scenario)
    r = {"metadata": spec, "candidates": points, "baselines": baselines,
         "algorithms": eliciters_descriptions}
    return r


@app.route("/<scenario>/ranges", methods=["GET"])
def get_ranges(scenario):
    """Report the candidates and their ranges for a particular scenario."""
    candidates, spec = _scenario(scenario)
    points, _collated = calc_ranges(candidates, spec)
    return jsonify(points)


@app.route("/<scenario>/baseline", methods=["GET"])
def get_baseline(scenario):
    """Return the performance baseline(s) of the scenario."""
    result = fileio.load_baseline(scenario)
    return jsonify(result)


@app.route("/<scenario>/constraints", methods=["PUT"])
def apply_constraints(scenario):
    """Apply constraints chosen by the user."""
    # TODO: placeholder
    # _ = request.get_json(force=True)
    return "OK"


@app.route("/<scenario>/choice", methods=["GET", "PUT"])
def get_choice(scenario):
    """Inform the front-end of the current eliciter choices."""
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
        if not eliciter.terminated():
            choice = [v.name for v in eliciter.query()]
            if (x in choice):  # and (y in choice) and (x != y):
                eliciter.put(x)

    # now give some new choices
    if eliciter.terminated():
        result = eliciter.result()
        res = {
            result.name: {
                "attr": result.attributes,
                "spec": result.spec_name
            }
        }
        log.add_result(res)
        data = log.log
        if not os.path.exists("logs"):
            os.mkdir("logs")
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
            pdf.cell(200, 10, txt=lines, ln=1, align="C")
        pdf.output(f"logs/{str(session['id'])}.pdf")
    else:
        res = []
        for option in eliciter.query():
            res.append({"name": option.name, "values": option.attributes})
        log.add_options(res)
    db.eliciter = eliciter
    db.logger = log
    return jsonify(res)
