import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from src.models import ResearchResponseModel

load_dotenv()

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = "fairy"
COLLECTION_NAME = "research_results"

def get_db():
    client = MongoClient(MONGODB_URI)
    return client[DATABASE_NAME]

def save_research_result(research: ResearchResponseModel, keyword: str, urls: list | None = None):
    db = get_db()
    collection = db[COLLECTION_NAME]
    
    document = {
        "_id": str(research.uuid),
        "owner": research.owner,
        "keyword": keyword,
        "smart_message": research.smart_message,
        "full_message": research.full_message,
        "urls": urls or [],
        "time": research.time,
        "created_at": datetime.utcnow()
    }
    
    collection.insert_one(document)
    return document

def get_research_result(uuid: str):
    db = get_db()
    collection = db[COLLECTION_NAME]
    return collection.find_one({"_id": uuid})
