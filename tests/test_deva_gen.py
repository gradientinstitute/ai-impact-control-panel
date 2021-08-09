from click.testing import CliRunner
from deva.scripts.gen import cli
import traceback
from shutil import copyfile
import os

test_dir = 'tests/tmp'


def test_data_model():
    copyfile('scenarios/example/sim.toml',
             os.path.join(test_dir, 'sim.toml'))
    copyfile('scenarios/example/model.toml',
             os.path.join(test_dir, 'model.toml'))

    outfiles = [
            'data/test.csv',
            'data/train.csv',
            ]
    outfiles = [os.path.join(test_dir, f) for f in outfiles]
    for f in outfiles:
        if os.path.exists(f):
            os.remove(f)

    runner = CliRunner()
    result = runner.invoke(cli, [test_dir, 'data'])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0
    for f in outfiles:
        assert os.path.exists(f)

    model_outfiles = [
        'models/metrics_list0.toml',
        'models/metrics_list1.toml',
        'models/metrics_list2.toml',
        'models/metrics_list3.toml',
        'models/metrics_range0.toml',
        'models/metrics_range1.toml',
        'models/metrics_range2.toml',
        'models/metrics_set1.toml',
        'models/metrics_set2.toml',
        'models/model_list0.joblib',
        'models/model_list1.joblib',
        'models/model_list2.joblib',
        'models/model_list3.joblib',
        'models/model_range0.joblib',
        'models/model_range1.joblib',
        'models/model_range2.joblib',
        'models/model_set1.joblib',
        'models/model_set2.joblib',
        'models/params_list0.toml',
        'models/params_list1.toml',
        'models/params_list2.toml',
        'models/params_list3.toml',
        'models/params_range0.toml',
        'models/params_range1.toml',
        'models/params_range2.toml',
        'models/params_set1.toml',
        'models/params_set2.toml',
        'models/scored_list0.csv',
        'models/scored_list1.csv',
        'models/scored_list2.csv',
        'models/scored_list3.csv',
        'models/scored_range0.csv',
        'models/scored_range1.csv',
        'models/scored_range2.csv',
        'models/scored_set1.csv',
        'models/scored_set2.csv']

    model_outfiles = [os.path.join(test_dir, f) for f in model_outfiles]
    for f in model_outfiles:
        if os.path.exists(f):
            os.remove(f)
    runner = CliRunner()
    result = runner.invoke(cli, [test_dir, 'model'])
    if result.exception:
        traceback.print_exception(*result.exc_info)
    assert result.exit_code == 0

    for f in model_outfiles:
        assert os.path.exists(f)
