import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from src.models import ResearchResponseModel

load_dotenv()

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = "fairy"
COLLECTION_NAME = {
    "RESEARCH_RESULTS": "research_results",
    "USERS": "users"
}

def get_db():
    client = MongoClient(MONGODB_URI)
    return client[DATABASE_NAME]

def save_research_result(research: ResearchResponseModel):
    db = get_db()
    collection = db[COLLECTION_NAME["RESEARCH_RESULTS"]]
    
    document = research.model_dump()
    document["_id"] = str(research.uuid)
    
    # Ensure created_at is present
    if "created_at" not in document or not document["created_at"]:
        document["created_at"] = datetime.utcnow()
    
    collection.insert_one(document)
    return document

def get_research_result(uuid: str):
    db = get_db()
    collection = db[COLLECTION_NAME]
    return collection.find_one({"_id": uuid})
