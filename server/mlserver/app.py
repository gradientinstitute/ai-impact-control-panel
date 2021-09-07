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
    res = dict(model1=dict(name='inital_a', FPR=0.6),
               model2=dict(name='initial_b', FPR=0.5))
    return jsonify(res)


@app.route('/choice/<stage>/<x>')
def update(stage, x):
    new_state = session['responses'] + x
    session['responses'] = new_state
    # probably not needed because new object
    # session.modified = True
    res = dict(model1=dict(name=new_state + '_a', FPR=0.6),
               model2=dict(name=new_state + '_b', FPR=0.5))
    return jsonify(res)
