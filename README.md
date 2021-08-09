# Oversight-prototype

Prototype code for the Minderoo oversight tool project.

Copyright 2021 Gradient Institute Ltd.


## Installation

1. Install python-poetry
2. run `poetry install` in this directory

Note: there is no need to do a pip install -e . : this happens automatically, 
along with venv creation and dependencies.

To get into a venv, do `poetry shell`.

## Generating data and models

`deva-gen` is the command for generating. See the --help.

It takes a scenario folder -- see `scenario/example` for an example.

For generating data, run:

`deva-gen scenarios/example data`

For a model on that data:

`deva-gen scenarios/example model`

## Data and Model configs

See the example scenario for commented versions of the configs.

## Running the dash

Currently just a skeleton, but try:

`deva-dash`

## Testing

In the venv, run `pytest`.
