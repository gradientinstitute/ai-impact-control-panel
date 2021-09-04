from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/choice")
def initial_view():
    return jsonify(model1='initial_a', model2='inital_b')


@app.route("/choice/<x>")
def update(x):
    return jsonify(model1='last_choice_' + x + 'a',
                   model2='last_choice_' + x + 'b')
