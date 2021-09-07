from flask import Flask, session, jsonify
from os import urandom

app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(16)


@app.route('/choice')
def initial_view():
    # set up some new state
    session['responses'] = ''
    # note if you mutate an object inside session, you have to tell it.
    session.modified = True
    return jsonify(model1='initial_a', model2='inital_b')


@app.route('/choice/<stage>/<x>')
def update(stage, x):
    new_state = session['responses'] + x
    session['responses'] = new_state
    # probably not needed because new object
    # session.modified = True
    return jsonify(model1=new_state + '_a',
                   model2=new_state + '_b')
