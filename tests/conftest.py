import os

import jsonpickle.handlers
import numpy as np
import pandas as pd
import pytest
from incense import ExperimentLoader
from sacred import Experiment as SacredExperiment
from sacred.observers import MongoObserver


def get_mongo_uri():
    in_devcontainer = (
        os.environ.get("TERM_PROGRAM") == "vscode"
        or os.environ.get("HOME") == "/home/vscode"
        or (os.environ.get("PATH") or "").startswith("/home/vscode")
    )
    if in_devcontainer:
        return "mongodb://mongo:27017"
    else:
        return None


MONGO_URI = get_mongo_uri()

TEST_DB_NAME = "incense_test"
RECENT_DB_NAME = "incense_recent_test"
DELETE_DB_NAME = "incense_delete_test"
HETEROGENOUS_DB_NAME = "incense_heterogenous_test"
INFO_DB_NAME = "incense_info_test"


@pytest.fixture
def loader():
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name=TEST_DB_NAME)
    return loader


@pytest.fixture
def delete_mongo_observer():
    observer = MongoObserver(url=MONGO_URI, db_name=DELETE_DB_NAME)
    return observer


@pytest.fixture
def delete_db_loader():
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name=DELETE_DB_NAME)
    return loader


@pytest.fixture
def recent_mongo_observer():
    observer = MongoObserver(url=MONGO_URI, db_name=RECENT_DB_NAME)
    return observer


@pytest.fixture
def recent_db_loader():
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name=RECENT_DB_NAME)
    return loader


@pytest.fixture
def heterogenous_mongo_observer():
    observer = MongoObserver(url=MONGO_URI, db_name=HETEROGENOUS_DB_NAME)
    return observer


@pytest.fixture
def heterogenous_db_loader():
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name=HETEROGENOUS_DB_NAME)
    return loader


@pytest.fixture
def info_mongo_observer():
    observer = MongoObserver(url=MONGO_URI, db_name=INFO_DB_NAME)
    return observer


@pytest.fixture
def info_db_loader():
    # Unregister handlers to simulate that sacred is not currently imported.
    jsonpickle.handlers.unregister(np.ndarray)
    jsonpickle.handlers.unregister(pd.DataFrame)
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name=INFO_DB_NAME)
    return loader


@pytest.fixture
def info_db_loader_pickled():
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name=INFO_DB_NAME, unpickle=False)
    return loader


@pytest.fixture
def add_exp_to_db():
    def inner(delete_mongo_observer, config_value):
        ex = SacredExperiment("name")
        ex.observers.append(delete_mongo_observer)
        ex.add_config({"value": config_value})

        def run_fn(value, _run):
            _run.log_scalar("test_metric", 1)
            _run.add_artifact(__file__)
            return value

        ex.main(run_fn)
        run = ex.run()
        return run._id

    return inner
