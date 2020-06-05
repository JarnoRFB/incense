# -*- coding: future_fstrings -*-
import collections.abc
from datetime import datetime
from fractions import Fraction

import numpy as np
import pandas as pd
import pytest
import sacred
from numpy.testing import assert_array_equal
from pandas.testing import assert_frame_equal
from pytest import raises
from sacred import Experiment


def test_repr(loader):
    exp = loader.find_by_id(3)
    assert repr(exp) == "Experiment(id=3, name=example)"


def test_metrics(loader):
    exp = loader.find_by_id(3)
    metric_names = ["training_loss", "training_accuracy", "test_loss", "test_accuracy"]
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
    # Sort for py35 compatibility.
    for x, y in zip(sorted(exp.keys()), sorted(exp_dict.keys())):
        assert x == y


def test_delete(delete_db_loader, delete_mongo_observer):
    # Add experiment to db.
    ex = Experiment("to be deleted")
    ex.observers.append(delete_mongo_observer)
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


def test_immutability__should_raise_type_error_on_item_access(loader):
    exp = loader.find_by_id(2)
    with raises(TypeError):
        exp.meta["command"] = "mutate"


def test_immutability__should_raise_attribute_error_on_attribute_access(loader):
    exp = loader.find_by_id(2)
    with raises(AttributeError):
        exp.meta.command = "mutate"


def test_info(info_db_loader, info_db_loader_pickled, info_mongo_observer):
    # Add experiment to db.
    ex = Experiment("info experiment")
    ex.observers.append(info_mongo_observer)
    ex.add_config({"value": 1})

    def run(value, _run):
        _run.info["number"] = 13
        _run.info["list"] = [1, 2]
        _run.info["object"] = Fraction(3, 4)
        return value

    ex.main(run)
    ex.run()
    # Retrieve and delete experiment.
    exp_unpickled = info_db_loader.find_by_id(1)
    exp_pickled = info_db_loader_pickled.find_by_id(1)

    assert exp_unpickled.info["number"] == exp_pickled.info["number"] == 13
    assert exp_unpickled.info["list"] == exp_pickled.info["list"] == [1, 2]
    assert exp_unpickled.info["object"] == Fraction(3, 4)
    assert isinstance(exp_pickled.info["object"], collections.abc.Mapping)

    exp_unpickled.delete(confirmed=True)


@pytest.fixture
def experiment_with_numpy_in_info(info_mongo_observer, info_db_loader) -> sacred.run.Run:
    # Add experiment to db.
    ex = Experiment("info experiment")
    ex.observers.append(info_mongo_observer)
    ex.add_config({"value": 1})

    def run(value, _run):
        _run.info["array"] = np.array([1, 2, 3])
        return value

    ex.main(run)
    yield ex.run()

    # Retrieve and delete experiment.
    info_db_loader.find_by_id(1).delete(confirmed=True)


def test_info_allows_restoring_numpy_arrays(experiment_with_numpy_in_info, info_db_loader):
    exp_unpickled = info_db_loader.find_by_id(experiment_with_numpy_in_info._id)
    assert_array_equal(exp_unpickled.info["array"], experiment_with_numpy_in_info.info["array"])


@pytest.fixture
def experiment_with_pandas_in_info(info_mongo_observer, info_db_loader) -> sacred.run.Run:
    # Add experiment to db.
    ex = Experiment("info experiment")
    ex.observers.append(info_mongo_observer)
    ex.add_config({"value": 1})

    def run(value, _run):
        _run.info["dataframe"] = pd.DataFrame({"a": [1, 2, 3], "b": ["1", "2", "3"]})
        return value

    ex.main(run)
    yield ex.run()

    # Retrieve and delete experiment.
    info_db_loader.find_by_id(1).delete(confirmed=True)


def test_info_allows_restoring_pandas_dataframes(experiment_with_pandas_in_info, info_db_loader):
    exp_unpickled = info_db_loader.find_by_id(experiment_with_pandas_in_info._id)
    assert_frame_equal(exp_unpickled.info["dataframe"], experiment_with_pandas_in_info.info["dataframe"])
