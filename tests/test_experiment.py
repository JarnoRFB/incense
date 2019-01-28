from datetime import datetime
import pandas as pd


def test_repr(loader):
    exp = loader.find_by_id(3)
    assert repr(exp) == 'Experiment(id=3, name=example)'


def test_metrics(loader):
    exp = loader.find_by_id(3)
    metric_names = [
        'training_loss',
        'training_acc',
        'test_loss',
        'test_acc'
    ]
    for metric_name in metric_names:
        assert metric_name in exp.metrics.keys()
        assert isinstance(exp.metrics[metric_name], pd.Series)
        assert exp.metrics[metric_name].name == metric_name
        assert exp.metrics[metric_name].index.name == 'step'


def test_metrics_len(loader):
    exp1 = loader.find_by_id(1)
    assert len(exp1.metrics['training_loss']) == 1

    exp2 = loader.find_by_id(2)
    assert len(exp2.metrics['training_loss']) == 3


def test_dotted_attribute_access(loader):
    exp = loader.find_by_id(2)
    assert exp.config.epochs == 3
    assert exp.experiment.name == 'example'
    assert exp.experiment.mainfile == 'conduct.py'

    assert isinstance(exp.start_time, datetime)
    assert isinstance(exp.result, float)


def test_item_attribute_access(loader):
    exp = loader.find_by_id(2)
    assert exp.config['epochs'] == 3
    assert exp.experiment['name'] == 'example'
    assert exp.experiment['mainfile'] == 'conduct.py'


def test_to_dict(loader):
    exp = loader.find_by_id(2)
    exp_dict = exp.to_dict()
    assert isinstance(exp_dict, dict)
    assert exp.keys() == exp_dict.keys()
