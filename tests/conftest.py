import os
from pathlib import Path
import pytest
from dotenv import load_dotenv

from incense import ExperimentLoader


@pytest.fixture
def loader():
    env_path = Path('..') / 'infrastructure' / 'sacred_setup' / '.env'
    load_dotenv(dotenv_path=env_path)
    loader = ExperimentLoader(
        mongo_uri=f'mongodb://{os.environ["MONGO_INITDB_ROOT_USERNAME"]}:{os.environ["MONGO_INITDB_ROOT_PASSWORD"]}@localhost:27017/?authMechanism=SCRAM-SHA-1',
        db_name=os.environ['MONGO_DATABASE'])
    return loader
