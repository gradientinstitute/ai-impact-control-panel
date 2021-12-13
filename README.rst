###################
Oversight-prototype
###################

Prototype code for the Minderoo oversight tool project.

Copyright 2021 Gradient Institute Ltd.

**************************************
What is this purpose of this software?
**************************************

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


*******
Running
*******

0. You'll need docker and docker-compose installed to run the app locally.
1. Place your scenario information in the ``scenarios`` folder, which will be
   mounted by docker compose.
2. Optionally, see the instructions below for generating some demo scenarios.
3. Run ``docker-compose up`` which should build and run the containers
   required.
4. Access ``http://localhost:3000`` in your browser for the app.


***********
Development
***********

Installation
------------

1. Install python-poetry
2. run ``poetry install`` in this directory

Note: there is no need to do a pip install -e . : this happens automatically, 
along with venv creation and dependencies.

To get into a venv, do ``poetry shell``.


Data and Model configs
----------------------

See the example scenarios for commented versions of the configs.


Running the server for development
----------------------------------

Go to the server folder. start the backend with ``server/mlserver/run_dev.sh``

To start the frontend, go to ``server/deva-ts`` and from there run ``yarn
start``.


Testing
-------

In the venv, run ``pytest``.
