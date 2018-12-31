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

