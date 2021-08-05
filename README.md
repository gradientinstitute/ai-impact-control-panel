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

It takes a problem file (e.g. vanilla.toml) which specifies the model config
etc. It has `data` and `model` subcommands for generating each of those. By
default it outputs into the data folder.

## Running the dash

Currently just a skeleton, but try:

`deva-dash`

## Testing

In the venv, run `pytest`.
