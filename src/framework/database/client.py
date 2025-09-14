from pymongo import MongoClient
import yaml
import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

config_path = os.path.join(PROJECT_ROOT, "config", "config.yaml")
# Load config
with open(config_path) as f:
    config = yaml.safe_load(f)

client = MongoClient(config["mongo_uri"])
db = client[config["database"]]
