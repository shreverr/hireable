from pymongo import MongoClient
from os import getenv

if getenv("MONGO_URI"):
    client = MongoClient(getenv("MONGO_URI"))
    db = client.get_database()
    print("Database connected successfully")
else:
    raise ValueError("MONGO_URI not found")