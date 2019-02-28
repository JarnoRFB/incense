import os
from pathlib import Path
import pytest
from dotenv import load_dotenv
from sacred.observers import MongoObserver
from incense import ExperimentLoader


@pytest.fixture
def loader():
    is_travis = 'TRAVIS' in os.environ
    env_path = Path('infrastructure') / 'sacred_setup' / '.env'
    load_dotenv(dotenv_path=env_path)
    if is_travis:
        mongo_uri = None
    else:
        mongo_uri = f'mongodb://{os.environ["MONGO_INITDB_ROOT_USERNAME"]}:{os.environ["MONGO_INITDB_ROOT_PASSWORD"]}@localhost:27017/?authMechanism=SCRAM-SHA-1'
    loader = ExperimentLoader(
        mongo_uri=mongo_uri,
        db_name='incense_test')
    return loader


@pytest.fixture
def mongo_observer():
    is_travis = 'TRAVIS' in os.environ
    env_path = Path('infrastructure') / 'sacred_setup' / '.env'
    load_dotenv(dotenv_path=env_path)
    if is_travis:
        mongo_uri = None
    else:
        mongo_uri = f'mongodb://{os.environ["MONGO_INITDB_ROOT_USERNAME"]}:{os.environ["MONGO_INITDB_ROOT_PASSWORD"]}@localhost:27017/?authMechanism=SCRAM-SHA-1'
    observer = MongoObserver.create(
        url=mongo_uri,
        db_name='incense_delete_test')
    return observer


@pytest.fixture
def delete_db_loader():
    is_travis = 'TRAVIS' in os.environ
    env_path = Path('infrastructure') / 'sacred_setup' / '.env'
    load_dotenv(dotenv_path=env_path)
    if is_travis:
        mongo_uri = None
    else:
        mongo_uri = f'mongodb://{os.environ["MONGO_INITDB_ROOT_USERNAME"]}:{os.environ["MONGO_INITDB_ROOT_PASSWORD"]}@localhost:27017/?authMechanism=SCRAM-SHA-1'
    loader = ExperimentLoader(
        mongo_uri=mongo_uri,
        db_name='incense_delete_test')
    return loader
