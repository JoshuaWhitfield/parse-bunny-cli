# utils/db.py
from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["parsebunny"]
collection = db["logs"]

def insert_log(command_name, payload):
    doc = {
        "command": command_name,
        "payload": payload,
        "status": "success"
    }
    collection.insert_one(doc)

def get_all_logs():
    return list(collection.find())
