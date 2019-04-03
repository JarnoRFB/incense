import pytest
from sacred.observers import MongoObserver
from incense import ExperimentLoader


@pytest.fixture
def loader():
    loader = ExperimentLoader(mongo_uri=None, db_name="incense_test")
    return loader


@pytest.fixture
def mongo_observer():
    observer = MongoObserver.create(url=None, db_name="incense_delete_test")
    return observer


@pytest.fixture
def delete_db_loader():
    loader = ExperimentLoader(mongo_uri=None, db_name="incense_delete_test")
    return loader
