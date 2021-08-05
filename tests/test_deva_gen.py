from click.testing import CliRunner
from deva.scripts.gen import cli

import os

test_dir = 'tests/tmp'


def test_data_model():
    outfiles = [
            'example_ctsperson_test.csv',
            'example_ctsperson_train.csv',
            'example_transaction_test.csv',
            'example_transaction_train.csv',
            'example_dscperson_test.csv',
            'example_dscperson_train.csv',
            ]
    for f in outfiles:
        p = os.path.join(test_dir, f)
        if os.path.exists(p):
            os.remove(p)

    runner = CliRunner()
    result = runner.invoke(cli, ['-f', test_dir, 'example.toml', 'data'])
    assert result.exit_code == 0
    for f in outfiles:
        p = os.path.join(test_dir, f)
        assert os.path.exists(p)

    p = os.path.join(test_dir, 'example_model.joblib')
    if os.path.exists(p):
        os.remove(p)
    runner = CliRunner()
    result = runner.invoke(cli, ['-f', test_dir, 'example.toml', 'model'])
    assert result.exit_code == 0
    assert os.path.exists(p)
