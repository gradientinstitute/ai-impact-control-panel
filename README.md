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

## Running an interactive demo

Run `deva-demo`,

Usage: `deva-demo [OPTIONS] SCENARIOS`

Options: 

`-m, --method [max|max_smooth|max_prim|rank|toy]`

Where `max` and `max_smooth` are active maximum-finding algorithms.
`max_smooth` refers to presenting smoothly varying queries to the user.
`max_prim` sorts the queries based on the value of a specified primary metric
(`primary_metric` in the metadata). `rank` is an active ranking algorithm, and
`toy` is a simple "follow the leader" style algorithm.

`-b, --bounds`

Ask about minimum performance bounds (will become its own demo/research fork in
the future).

`-f, --nofilter`                  

Do not apply Pareto efficient model filter.

`SCENARIO` is the folder location of the scenario models, e.g.
`scenarios/example`

## Testing

In the venv, run `pytest`.
