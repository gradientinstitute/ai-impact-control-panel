"""Flask backend elicitation server for AI Impact Control Panel."""

import os
import os.path
from util import jsonify, random_key

import redis
from flask import Flask, session, abort, request, send_from_directory

from deva import elicit, fileio, logger, compareBase
from deva import bounds
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
    res = {"tasks": ["deployment", "boundaries"]}
    return jsonify(res)


@app.route("/images/<scenario>/<path:name>")
def send_image(scenario, name):
    """Send target image to client."""
    scenario_path = os.path.join(fileio.repo_root(),
                                 f"scenarios/{scenario}/images")
    return send_from_directory(scenario_path, name)


@app.route("/deployment/logs/<ftype>")
def send_log(ftype):
    """Send a completed session logfile to the user."""
    if ftype not in db.logger.files:
        abort(404)  # incorrect usage

    full_path = db.logger.files[ftype]
    path, filename = os.path.split(full_path)
    return send_from_directory(path, filename)


@app.route("/scenarios")
def get_scenarios():
    """Get all scenarios in server folder."""
    data = fileio.list_scenarios()
    return jsonify(data)


def _scenario(name):
    """Get the data for a particular scenario."""
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


@app.route("/scenarios/<scenario>")
def get_info(scenario):
    """Get all info about a particular scenario."""
    candidates, spec = _scenario(scenario)
    points, _ = calc_ranges(candidates, spec)
    r = {"metadata": spec, "candidates": points,
         "algorithms": eliciters_descriptions}
    return r


def _get_boundary_sample():
    """Get a couple of samples from the boundary eliciter."""
    sampler = db.bounder
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
    return res


@app.route("/boundaries/new", methods=["PUT"])
def init_bounds():
    """Initialise a bounds elicitation session."""
    if "id" not in session:
        session["id"] = random_key(16)

    data = request.get_json(force=True)

    scenario = data["scenario"]
    constraints = data["constraints"]
    _algo = data["algorithm"]
    _user = data["user"]

    # Boundary elicitation not currently exposed.
    candidates, meta = _scenario(scenario)
    baseline = meta["baseline"]
    metrics = meta["metrics"]
    attribs, table = bounds.tabulate(candidates, metrics)
    ref = [baseline["industry_average"][a] for a in attribs]
    db.bounder = bounds.PlaneSampler(ref, table, attribs, steps=30)

    # get initial choice
    res = _get_boundary_sample()

    # res = jsonify({})
    return res


@app.route("/boundaries/choice", methods=["PUT"])
def get_bounds_choice():
    """Accept the user's choice for a bounds elicitation session."""
    if db.bounder is None:
        print("Session not initialised!")
        abort(400)  # Not initialised
    sampler = db.bounder

    # we received a choice, process it
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

    # now send a new choice
    res = _get_boundary_sample()
    return jsonify(res)


@app.route("/deployment/new", methods=["PUT"])
def make_new_deployment_session():
    """Initialise an eliciter with a particular algorithm and scenario."""
    print(f"new deployment got payload {request}")
    if "id" not in session:
        session["id"] = random_key(16)

    # get info about setup from the frontend
    data = request.get_json(force=True)
    scenario = data["scenario"]
    algo = data["algorithm"]
    name = data["name"]

    # assume that a reload means user wants a restart
    print("Init new session for user")
    candidates, spec = _scenario(scenario)
    eliciter = elicit.algorithms[algo](candidates, spec)
    log = logger.Logger(scenario, algo, name, spec["metrics"])
    db.eliciter = eliciter
    db.logger = log
    # send our first sample of candidates
    res = _get_deployment_choice(eliciter, log)
    return jsonify(res)


def _get_deployment_choice(eliciter, log):

    if not eliciter.terminated():
        res = []
        for option in eliciter.query():
            res.append({"name": option.name, "values": option.attributes})
    else:
        log.result = eliciter.result()
        log.write()
        res = {}

    return res


@app.route("/deployment/choice", methods=["PUT"])
def get_choice():
    """Inform the front-end of the current eliciter choices."""
    if db.eliciter is None:
        print("Session not initialised!")
        abort(400)  # Not initialised

    eliciter = db.eliciter
    log = db.logger

    res = {}

    data = request.get_json(force=True)
    # log.add_choice([data])
    x = data["first"]

    # Only pass valid choices on to the eliciter
    if not eliciter.terminated():
        choice = [v.name for v in eliciter.query()]
        if (x in choice):  # and (y in choice) and (x != y):
            log.choice(eliciter.query(), data)
            eliciter.put(x)

    # have to check again because now it might be terminated
    # after we added a new choice above
    res = _get_deployment_choice(eliciter, log)

    # Write back to database
    db.eliciter = eliciter
    db.logger = log

    return jsonify(res)


@app.route("/deployment/result")
def get_result():
    """Get the eliciter result, if it exists."""
    eliciter = db.eliciter
    if eliciter.terminated():
        result = eliciter.result()
        res = {
            result.name: {
                "attr": result.attributes,
                "spec": result.spec_name
            }
        }
    else:
        res = {}
    return jsonify(res)
