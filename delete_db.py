import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient

env_path = Path(".") / "infrastructure" / "sacred_setup" / ".env"
load_dotenv(dotenv_path=env_path)

DB_NAME = os.environ["MONGO_DATABASE"]

client: MongoClient = MongoClient(host="mongo")
client.drop_database(DB_NAME)

shutil.rmtree(Path("~/data/incense_test/").expanduser(), ignore_errors=True)

print(f"Database {DB_NAME} successfully deleted.")
