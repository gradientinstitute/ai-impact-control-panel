Oversight-prototype
===================

Prototype code for the Minderoo oversight tool project.

Copyright 2021 Gradient Institute Ltd.


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
