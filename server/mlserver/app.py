from flask import Flask, session, jsonify, abort
# from flask_caching import Cache
from deva import elicit
from deva import fileio
import random
import string


def random_key(n):
    """Make a random string of n characters."""
    return ''.join(random.choice(string.ascii_letters) for i in range(n))


# Set up the flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = random_key(16)

# todo: find some sort of persistent cache
eliciters = {}
scenarios = {}


def _scenario(name="pareto"):
    global scenarios

    if name not in scenarios:
        data = fileio.load_scenario(name, False)

        # Massage the metadata
        models, spec = data
        for attr in spec:
            spec[attr]["name"] = attr  # uid may differ in the future
            for key in spec[attr]:
                # get rid of my plural adjustments for now
                if isinstance(spec[attr][key], str):
                    spec[attr][key] = spec[attr][key].format(s="s")

        for m in models:
            # make html-friendly uuid
            m.name = m.name.replace(" ", "_")

        scenarios[name] = (models, spec)

    return scenarios[name]


@app.route('/metadata')
def meta():
    # TODO - have scenario specific endpoints?
    # Perhaps accessing one also sets your next session's scenario?
    return _scenario()[1]


@app.route('/choice')
def initial_view():
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
    candidates, _ = _scenario()
    eliciter = elicit.ActiveMax(candidates)  # TODO: user choice?
    eliciters[session["ID"]] = eliciter

    # send the performance and choices to the frontend
    assert isinstance(eliciter.query, elicit.Pair)
    m1, m2 = eliciter.query
    return jsonify({m1.name: m1.attributes, m2.name: m2.attributes})


@app.route('/choice/<x>/<y>')
def update(x, y):
    global eliciters

    if "ID" not in session:
        print("Session not initialised!")
        abort(400)  # Not initialised

    eliciter = eliciters[session["ID"]]

    # Only pass valid choices on to the eliciter
    if not eliciter.terminated:
        choice = eliciter.query
        if (x in choice) and (y in choice) and (x != y):
            eliciter.input(x)

    if eliciter.terminated:
        # terminate by sending a single model
        result = eliciter.result
        res = {result.name: result.attributes}
    else:
        # eliciter has not terminated - extract the next choice
        assert isinstance(eliciter.query, elicit.Pair)
        m1, m2 = eliciter.query
        res = {m1.name: m1.attributes, m2.name: m2.attributes}

    return jsonify(res)
