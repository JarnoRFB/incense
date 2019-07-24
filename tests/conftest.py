import os

import pytest
from sacred.observers import MongoObserver

from incense import ExperimentLoader

from .utils import get_mongo_uri


def get_mongo_uri():
    if "TRAVIS" in os.environ:
        return None
    else:
        return "mongodb://mongo:27017"


MONGO_URI = get_mongo_uri()


@pytest.fixture
def loader():
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name="incense_test")
    return loader


@pytest.fixture
def delete_mongo_observer():
    observer = MongoObserver.create(url=MONGO_URI, db_name="incense_delete_test")
    return observer


@pytest.fixture
def delete_db_loader():
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name="incense_delete_test")
    return loader


@pytest.fixture
def recent_mongo_observer():
    observer = MongoObserver.create(url=MONGO_URI, db_name="incense_recent_test")
    return observer


@pytest.fixture
def recent_db_loader():
    loader = ExperimentLoader(mongo_uri=MONGO_URI, db_name="incense_recent_test")
    return loader
