import os
from pymongo import MongoClient
from dotenv import load_dotenv
from uuid import UUID
from datetime import datetime

load_dotenv()

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = "fairy"
COLLECTION_NAME = "research_results"

def get_db():
    client = MongoClient(MONGODB_URI)
    return client[DATABASE_NAME]

def save_research_result(uuid: UUID, owner: int, keyword: str, smart_message: str, full_message: str, urls: list, time: float):
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    document = {
        "_id": str(uuid),
        "owner": owner,
        "keyword": keyword,
        "smart_message": smart_message,
        "full_message": full_message,
        "urls": urls,
        "time": time,
        "created_at": datetime.utcnow()
    }
    
    collection.insert_one(document)
    return document

def get_research_result(uuid: str):
    db = get_db()
    collection = db[COLLECTION_NAME]
    return collection.find_one({"_id": uuid})
