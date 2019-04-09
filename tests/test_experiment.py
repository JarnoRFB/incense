# -*- coding: future_fstrings -*-
from datetime import datetime

import pandas as pd
from pytest import raises
from sacred import Experiment


def test_repr(loader):
    exp = loader.find_by_id(3)
    assert repr(exp) == "Experiment(id=3, name=example)"


def test_metrics(loader):
    exp = loader.find_by_id(3)
    metric_names = ["training_loss", "training_acc", "test_loss", "test_acc"]
    for metric_name in metric_names:
        assert metric_name in exp.metrics.keys()
        assert isinstance(exp.metrics[metric_name], pd.Series)
        assert exp.metrics[metric_name].name == metric_name
        assert exp.metrics[metric_name].index.name == "step"


def test_metrics_len(loader):
    exp1 = loader.find_by_id(1)
    assert len(exp1.metrics["training_loss"]) == 1

    exp2 = loader.find_by_id(2)
    assert len(exp2.metrics["training_loss"]) == 3


def test_dotted_attribute_access(loader):
    exp = loader.find_by_id(2)
    assert exp.config.epochs == 3
    assert exp.experiment.name == "example"
    assert exp.experiment.mainfile == "conduct.py"

    assert isinstance(exp.start_time, datetime)
    assert isinstance(exp.result, float)


def test_item_attribute_access(loader):
    exp = loader.find_by_id(2)
    assert exp.config["epochs"] == 3
    assert exp.experiment["name"] == "example"
    assert exp.experiment["mainfile"] == "conduct.py"


def test_to_dict(loader):
    exp = loader.find_by_id(2)
    exp_dict = exp.to_dict()
    assert isinstance(exp_dict, dict)
    assert exp.keys() == exp_dict.keys()


def test_delete(delete_db_loader, mongo_observer):
    # Add experiment to db.
    ex = Experiment("to be deleted")
    ex.observers.append(mongo_observer)
    ex.add_config({"value": 1})

    def run(value, _run):
        _run.log_scalar("test_metric", 1)
        _run.add_artifact(__file__)
        return value

    ex.main(run)
    ex.run()
    # Retrieve and delete experiment.
    exp = delete_db_loader.find_by_id(1)
    exp.delete(confirmed=True)
    # Make sure experiment cannot be retrieved again.
    with raises(ValueError):
        exp = delete_db_loader.find_by_id(1)


def test_delete_prompt(loader, monkeypatch):
    """Check that experiment is not deleted if prompt is answered with 'N'."""
    exp = loader.find_by_id(1)
    with monkeypatch.context() as m:
        m.setattr("builtins.input", lambda x: "N")
        exp.delete()
    loader.find_by_id.cache_clear()
    exp = loader.find_by_id(1)
    assert exp.id == 1
