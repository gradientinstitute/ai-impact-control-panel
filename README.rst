Oversight-prototype
===================

Prototype code for the Minderoo oversight tool project.

Copyright 2021 Gradient Institute Ltd.

What is this purpose of this software?
--------------------------------------

Today, there are many AI systems making consequential decisions which affect our
lives and livelihoods. Your bank runs AI systems to assess your credit risk for
loans, your Government uses AI systems for law enforcement, your job site uses
AI to determine your rank in a list of candidates, and your news feed uses AI to
target your views about politics or public health.

AI systems come with novel risk of harms. AI obeys the letter, not the intent
of instructions. It views the world only via the data we give it. It has no
minimum moral constraints, and no understanding of the context. It can make
millions of decisions every second.

We believe a new class of technical tooling, or AI governance software, is
needed to control for these risks. One of the key causes of harm is the
extremely narrow objectives given to an AI model. AI systems operate with
mathematical objectives, so to control for any kind of risk of a system, harms
and benefits must be quantified. That may sound too difficult for human
decision makers. But just because you ignore the trade-offs an AI system makes
- doesn't mean the system isn't making them.

This AI Governance Software supports informed decisions about the objectives and
constraints of the system - in light of the identified harms and benefits. It
helps to ensure the accountable business entity, not the technical developer,
set the balance of objectives and seeks clear acceptable limits of risk from a
compliance function.  The software keeps an audit trail of the deployment
decisions made, which are indispensable for auditors, regulators, researchers
and indeed affected communities.


Installation
------------

1. Install python-poetry
2. run ``poetry install`` in this directory

Note: there is no need to do a pip install -e . : this happens automatically, 
along with venv creation and dependencies.

To get into a venv, do ``poetry shell``.

Generating data
---------------

``deva-sim`` is the command for generating data. See the --help.

It takes a toml configuration file -- see ``data/fraud.toml`` for an example.

For generating data, run:

``deva-sim data/fraud.toml``

It will output ``data/fraud_train.csv`` and ``data/fraud_test.csv``.


Generating Scenarios
--------------------

These are fake clients, with their own candidate models trained on the data
To generate candidate models, run, for example:

``deva-gen scenarios/fraud``


Data and Model configs
----------------------

See the example scenario for commented versions of the configs.


Running the server
------------------

Go to the server folder. start the backend with ``server/mlserver/run.sh``

To start the frontend, go to ``server/deva-ts`` and from there run ``yarn
start``.


Running an interactive demo
---------------------------

Run ``deva-demo``,

Usage: ``deva-demo [OPTIONS] SCENARIOS``

Options: 

``-m, --method [max|max_smooth|max_prim|rank|toy]``

Where ``max`` and ``max_smooth`` are active maximum-finding algorithms.
``max_smooth`` refers to presenting smoothly varying queries to the user.
``max_prim`` sorts the queries based on the value of a specified primary metric
(``primary_metric`` in the metadata). ``rank`` is an active ranking algorithm,
and ``toy`` is a simple "follow the leader" style algorithm.

``-b, --bounds``

Ask about minimum performance bounds (will become its own demo/research fork in
the future).

``-f, --nofilter``                  

Do not apply Pareto efficient model filter.

``SCENARIO`` is the folder location of the scenario models, e.g.
``scenarios/example``

Testing
-------

In the venv, run ``pytest``.
