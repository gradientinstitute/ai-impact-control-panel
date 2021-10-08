from click.testing import CliRunner
from deva.scripts import gen, sim
import traceback
from shutil import copyfile
import os

test_dir = 'tests/tmp'


def test_data_model():
    copyfile('data/fraud.toml', os.path.join(test_dir, 'fraud.toml'))
    copyfile('scenarios/fraud/model.toml',
             os.path.join(test_dir, 'model.toml'))

    outfiles = [
            'fraud_test.csv',
            'fraud_train.csv',
            ]
    outfiles = [os.path.join(test_dir, f) for f in outfiles]
    for f in outfiles:
        if os.path.exists(f):
            os.remove(f)

    runner = CliRunner()
    result = runner.invoke(sim.cli, [os.path.join(test_dir, 'fraud.toml')])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    for f in outfiles:
        assert os.path.exists(f)

    model_outfiles = [
        'models/metrics_logistic_list0.toml',
        'models/metrics_logistic_list1.toml',
        'models/metrics_logistic_list2.toml',
        'models/metrics_logistic_list3.toml',
        'models/model_logistic_list0.joblib',
        'models/model_logistic_list1.joblib',
        'models/model_logistic_list2.joblib',
        'models/model_logistic_list3.joblib',
        'models/params_logistic_list0.toml',
        'models/params_logistic_list1.toml',
        'models/params_logistic_list2.toml',
        'models/params_logistic_list3.toml',
        'models/scored_logistic_list0.csv',
        'models/scored_logistic_list1.csv',
        'models/scored_logistic_list2.csv',
        'models/scored_logistic_list3.csv']

    model_outfiles = [os.path.join(test_dir, f) for f in model_outfiles]
    for f in model_outfiles:
        if os.path.exists(f):
            os.remove(f)
    runner = CliRunner()
    result = runner.invoke(gen.cli, [test_dir, '--data-folder', test_dir])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0

    for f in model_outfiles:
        assert os.path.exists(f)
