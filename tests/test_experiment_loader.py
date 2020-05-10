# -*- coding: future_fstrings -*-
from pathlib import Path

import pytest
from pytest import raises
from sacred import Experiment as SacredExperiment

from incense.experiment import Experiment, FileSystemExperiment
from incense.experiment_loader import FileSystemExperimentLoader


def test_find_by_id(loader):
    exp = loader.find_by_id(1)
    assert isinstance(exp, Experiment)
    assert exp.id == 1


def test_find_by_ids(loader):
    exps = loader.find_by_ids([1, 2])
    for exp in exps:
        assert isinstance(exp, Experiment)
    assert len(exps) == 2


def test_find_by_name(loader):
    exps = loader.find_by_name("example")
    assert len(exps) == 3


def test_find_by_key(loader):
    exps = loader.find_by_key("config.optimizer", "adam")
    assert len(exps) == 1
    assert exps[0].config["optimizer"] == "adam"


def test_find_by_str_config_key(loader):
    exps = loader.find_by_config_key("optimizer", "adam")
    assert len(exps) == 1
    assert exps[0].config["optimizer"] == "adam"


def test_find_by_number_config_key(loader):
    exps = loader.find_by_config_key("epochs", 3)
    assert len(exps) == 1
    assert exps[0].config["epochs"] == 3


def test_find_all(loader):
    exps = loader.find_all()
    assert len(exps) == 3


def test_find_latest__with_newly_added_experiments(recent_db_loader, recent_mongo_observer):
    ex = SacredExperiment("most recent")
    ex.observers.append(recent_mongo_observer)
    ex.add_config({"value": 1})

    def run(value, _run):
        return value

    ex.main(run)
    ex.run()

    exp = recent_db_loader.find_latest()
    assert exp.config.value == 1

    ex = SacredExperiment("new most recent")
    ex.observers.append(recent_mongo_observer)
    ex.add_config({"value": 2})

    ex.main(run)
    ex.run()

    exp = recent_db_loader.find_latest()
    assert exp.config.value == 2


def test_find_latest__for_multiple_with_newly_added_experiments(recent_db_loader, recent_mongo_observer):
    ex = SacredExperiment("most recent")
    ex.observers.append(recent_mongo_observer)
    ex.add_config({"value": 1})

    def run(value, _run):
        return value

    ex.main(run)
    ex.run()

    ex = SacredExperiment("new most recent")
    ex.observers.append(recent_mongo_observer)
    ex.add_config({"value": 2})

    ex.main(run)
    ex.run()

    exps = recent_db_loader.find_latest(2)

    assert exps[0].config.value == 2
    assert exps[1].config.value == 1


def test_find(loader):
    exps = loader.find({"$and": [{"config.optimizer": "sgd"}, {"config.epochs": 3}]})
    assert len(exps) == 1
    assert exps[0].id == 2


def test_error_message_for_missing_id(loader):
    with raises(ValueError, match='Experiment with id 4 does not exist in database "incense_test".'):
        exp = loader.find_by_id(4)


class TestFileSystemExperimentLoader:
    @pytest.fixture
    def loader(self):
        return FileSystemExperimentLoader(Path("~/data/incense_test/").expanduser())

    def test_find_by_id(self, loader):
        exp = loader.find_by_id(1)
        assert isinstance(exp, FileSystemExperiment)
        assert exp.id == 1

    def test_error_message_for_missing_id(self, loader):
        with raises(ValueError, match="Experiment with id 4 does not exist in filesystems runs directory"):
            exp = loader.find_by_id(4)
