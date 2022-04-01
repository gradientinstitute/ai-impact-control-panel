# AI Impact Control Panel

An interactive application for decision-makers to help understand and control
the impacts of their AI systems. Developed by [Gradient Institute](https://gradientinstitute.org) with support from [Minderoo Foundation](https://www.minderoo.org).

Check out the [live demo](https://portal.gradientinstitute.org/aicontrolpanel)!

Read more about the tool in this [blog post](https://medium.com/gradient-institute/ai-impact-control-panel-8f2316505a1f).

**This code is at an Alpha (early) level of development: frequent and substantial changes in functionality are likely to occur.**


## What it does

<img src="images/control_panel_location.png"/>

This tool helps decision-makers understand and control the impacts of their AI
systems. Specifically, it helps them select between system 'candidates'. These
are potential configurations of the system that could be deployed. They might,
for example, be 

- different machine learning models (e.g. random forest, linear model)
- different hyperparameter settings (e.g. fairness regularization strength)
- different approaches entirely (e.g. human-based decision-making, machine
  learning).

The candidates are not generated by the control panel and form an input that
users must provide when configuring. In addition to these parameter settings,
the user must also supply the candidates' performances with respect to the
metrics they are using to evaluate the system. 

Given these inputs, the control panel provides decision-makers

- an interactive interface to visualise different system 'candidates' and their
  impacts, for example, where each candidate might be a different ML model that
  could be deployed, or a different algorithm configuration (decision
  thresholds, regularising parameters, strengths of different terms in the
  objective function)
- a filtering interface to rule out candidates that are obviously
  unacceptable
- an elicitation alogrithm that finds decision-makers' most-preferred candidate
  by asking a series of guided questions.
- a record of the questions posed by the tool and the decisions made by the user for the purpose of ensuring the reasons for choosing a given system can be explained.

A more in-depth description of the context and potential use-cases for the AI impact
control panel can be found in [this blog post](https://medium.com/gradient-institute/ai-impact-control-panel-8f2316505a1f).


## Prerequisites

The control panel does not actually build machine learning models, decide what
performance objectives your system should have, or evaluate those metrics on
test data. You'll need to provide

1. metadata explaining your system, including its objectives and performance
   measures

2. A set of files containing the values of the peformance measures for each
   candidate and their corresponding configuration values.

Have a look at the example systems in the `scenarios` folder. You'll need to
create a new scenario folder and provide the above information in a matching
format. The scenarios folder needs to containin

1. `metadata.toml`: gives all the information about the system and its metrics
2. `images/`: a folder of icons the frontand can use to illustrate
   performance metrics
3. `baseline.toml`: a set of baselines against which your candidates
   can be compared
4. `models/metrics_*.toml`: a file for each candidate (replace the star with
   a number or a name as approprate) giving the value of the performance
   metrics for that candidate
5. `models/params_*.toml`: a file for each candidate (with matching name to
   a metrics file) giving the value of any parameters used to generate the
   candidate.

The `jobs` example is well-commented and is a good place to start.

## Run the control panel

0. You'll need docker and docker-compose installed to run the app locally.
1. Place your scenario information in the `scenarios` folder, which will be
   mounted by docker compose.
3. Run `docker-compose up` from the root of the repo which should build and run the containers required.
4. Access `http://localhost/aicontrolpanel` in your browser for the app.

Note, there is a docker-compose-prod.yml which you should ignore (this is for
the live demo deployment).

## Development

If you'd like to get involved with development of this tool, we'd love to
collaborate: send us an email at `info@gradientinstitute.org`. Of course, you
may wish to just dive into the code: the instructions below should serve as
a starting point.

### Installing for development

Prerequisites:

1. python 3.8+
2. poetry (python package manager)
3. npm 8.5+
4. yarn 1.22+

Instructions:

1. run `poetry install` in this directory.
2. run `poetry shell` to start a new shell with the virtual environment
   enabled.
3. cd to `server/mlserver` and run `./run_dev.sh`. This will start the backend
   server.
4. Open a new shell, run `poetry shell` in the repo root directory, navigate to
   `server/deva-ts`.
5. Run `yarn install` to install the required packages then `yarn start` to serve the frontend.

### Testing

In the venv, run `make test`, `make lint` and `make typecheck`.


## Copyright and License

Copyright 2021-2022 Gradient Institute Ltd. <info@gradientinstitute.org>

Licensed under Apache 2 (see LICENSE file).
