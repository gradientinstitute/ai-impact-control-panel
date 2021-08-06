from click.testing import CliRunner
from deva.scripts.gen import cli
import traceback

import os

test_dir = 'tests/tmp'


def test_data_model():
    outfiles = [
            'example_sim_test.csv',
            'example_sim_train.csv',
            ]
    outfiles = [os.path.join(test_dir, f) for f in outfiles]
    for f in outfiles:
        if os.path.exists(f):
            os.remove(f)

    runner = CliRunner()
    result = runner.invoke(cli, ['--data-folder', test_dir,
                                 '--sim', 'example.sim',
                                 'data'])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    for f in outfiles:
        assert os.path.exists(f)

    model_outfiles = ['example_sim_trained_randomforest1.joblib',
                      'example_sim_scoredby_randomforest1.csv']
    model_outfiles = [os.path.join(test_dir, f) for f in model_outfiles]
    for f in model_outfiles:
        if os.path.exists(f):
            os.remove(f)
    runner = CliRunner()
    result = runner.invoke(cli, ['--data-folder', test_dir,
                                 '--sim', 'example.sim',
                                 'model', 'randomforest1.model'])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    for f in model_outfiles:
        assert os.path.exists(f)
