from pymongo import MongoClient
from datetime import datetime
from src.models import ResearchResponseModel
from src.config import config

MONGODB_URI = config.MONGODB_URI
DATABASE_NAME = "fairy"
COLLECTION_NAME = {
    "RESEARCH_RESULTS": "research_results",
    "USERS": "users"
}

def get_db():
    client = MongoClient(MONGODB_URI, uuidRepresentation='standard')
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
    collection = db[COLLECTION_NAME["RESEARCH_RESULTS"]]
    return collection.find_one({"_id": uuid})

def update_research_message_id(uuid: str, message_id: int, time: float = None):
    db = get_db()
    collection = db[COLLECTION_NAME["RESEARCH_RESULTS"]]
    update_data = {"message_id": message_id}
    if time is not None:
        update_data["time"] = time
    collection.update_one({"_id": uuid}, {"$set": update_data})

def get_research_by_message_id(message_id: int):
    db = get_db()
    collection = db[COLLECTION_NAME["RESEARCH_RESULTS"]]
    return collection.find_one({"message_id": message_id})

def init_db():
    """Initialize database indexes"""
    db = get_db()
    # Create index for user_id in research_results to optimize user-based queries
    db[COLLECTION_NAME["RESEARCH_RESULTS"]].create_index("user_id")
    # Create index for message_id to optimize follow-up research lookups
    db[COLLECTION_NAME["RESEARCH_RESULTS"]].create_index("message_id")
