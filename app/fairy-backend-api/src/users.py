from datetime import datetime
from src.db import get_db, COLLECTION_NAME
from src.models import UserModel

def get_user(user_id: int) -> UserModel | None:
    db = get_db()
    collection = db[COLLECTION_NAME["USERS"]]
    user_doc = collection.find_one({"user_id": user_id})
    if user_doc:
        return UserModel(**user_doc)
    return None

def create_or_update_tos(user_id: int) -> UserModel:
    db = get_db()
    collection = db[COLLECTION_NAME["USERS"]]
    
    user = get_user(user_id)
    now = datetime.utcnow()
    
    if user:
        collection.update_one(
            {"user_id": user_id},
            {"$set": {"tos_agreed": True, "updated_at": now}}
        )
        user.tos_agreed = True
        user.updated_at = now
        return user
    else:
        new_user = UserModel(
            user_id=user_id,
            tos_agreed=True,
            created_at=now,
            updated_at=now
        )
        collection.insert_one(new_user.model_dump())
        return new_user

def add_research_to_user(user_id: int, research_uuid: str):
    db = get_db()
    collection = db[COLLECTION_NAME["USERS"]]
    
    # Ensure user exists (should exist if they passed ToS check, but for safety)
    # If user doesn't exist here, it might be a logic error or first time usage without ToS (which shouldn't happen)
    # But per requirements "Update user data upon research including first time", 
    # if we enforce ToS first, the user should exist. 
    # However, let's handle the case where we just update/upsert.
    
    now = datetime.utcnow()
    
    collection.update_one(
        {"user_id": user_id},
        {
            "$push": {"research_list": research_uuid},
            "$set": {"updated_at": now},
            "$setOnInsert": {"created_at": now, "tos_agreed": False} # Default if created here, though should be True via ToS
        },
        upsert=True
    )
