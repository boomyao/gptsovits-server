from pymongo import MongoClient
import os

mongo_client = None
def get_client():
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/admin")
    return mongo_client

def get_collection(db_name, collection_name):
    # if not exist collection, create it
    client = get_client()
    db = client[db_name]
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)
    return db[collection_name]
