# -*- coding: future_fstrings -*-
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal
from pytest import raises


def test_projection_with_renaming(loader):
    exps = loader.find_by_ids([1, 2, 3])
    expected_projected_data = {"exp_id": [1, 2, 3], "epochs": [1, 3, 1], "optimizer": ["sgd", "sgd", "adam"]}
    expected_projected = pd.DataFrame(expected_projected_data).set_index("exp_id")
    projected = exps.project(on=["config.epochs", "config.optimizer"])

    assert_frame_equal(projected.sort_index(axis="columns"), expected_projected.sort_index(axis="columns"))


def test_projection_without_renaming(loader):
    exps = loader.find_by_ids([1, 2, 3])
    expected_projected_data = {
        "exp_id": [1, 2, 3],
        "config.epochs": [1, 3, 1],
        "config.optimizer": ["sgd", "sgd", "adam"],
    }
    expected_projected = pd.DataFrame(expected_projected_data).set_index("exp_id")
    projected = exps.project(on=["config.epochs", "config.optimizer"], rename=None)

    assert_frame_equal(projected.sort_index(axis="columns"), expected_projected.sort_index(axis="columns"))


def test_projection_with_aggregation(loader):
    exps = loader.find_by_ids([1, 2, 3])
    expected_projected_data = {
        "exp_id": [1, 2, 3],
        "epochs": [1, 3, 1],
        "training_loss_mean": [0.6407258245944977, 0.42567836346162685, 0.2221361954788367],
    }
    expected_projected = pd.DataFrame(expected_projected_data).set_index("exp_id")
    projected = exps.project(on=["config.epochs", {"metrics.training_loss": np.mean}])
    assert_frame_equal(projected.sort_index(axis="columns"), expected_projected.sort_index(axis="columns"))


def test_projection_with_heterogenous_formats(heterogenous_db_loader, heterogenous_mongo_observer, add_exp_to_db):
    id1 = add_exp_to_db(heterogenous_mongo_observer, config_value={"param1": 1})
    id2 = add_exp_to_db(heterogenous_mongo_observer, config_value={"param1": 2})
    id3 = add_exp_to_db(heterogenous_mongo_observer, config_value={"param2": 3})

    exps = heterogenous_db_loader.find_by_ids([id1, id2, id3])
    projected = exps.project(on=["config.value.param1"], on_missing="ignore")
    expected_projected = pd.DataFrame({"exp_id": [id1, id2, id3], "param1": [1, 2, None]}).set_index("exp_id")
    assert_frame_equal(projected, expected_projected)


def test_projection_with_heterogenous_formats__should_raise(
    heterogenous_db_loader, heterogenous_mongo_observer, add_exp_to_db
):
    id1 = add_exp_to_db(heterogenous_mongo_observer, config_value={"param1": 1})
    id2 = add_exp_to_db(heterogenous_mongo_observer, config_value={"param1": 2})
    id3 = add_exp_to_db(heterogenous_mongo_observer, config_value={"param2": 3})

    exps = heterogenous_db_loader.find_by_ids([id1, id2, id3])
    with raises(KeyError):
        projected = exps.project(on=["config.value.param1"])
