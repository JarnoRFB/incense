import pandas as pd


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
