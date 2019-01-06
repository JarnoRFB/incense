import os
from pathlib import Path
import pytest
from dotenv import load_dotenv

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
        db_name=os.environ['MONGO_DATABASE'])
    return loader
