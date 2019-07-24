import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

env_path = Path(".") / "infrastructure" / "sacred_setup" / ".env"
load_dotenv(dotenv_path=env_path)

DB_NAME = os.environ["MONGO_DATABASE"]

client = MongoClient(host="mongo")
client.drop_database(DB_NAME)
print(f"Database {DB_NAME} successfully deleted.")
