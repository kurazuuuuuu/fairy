import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.models import ResearchBodyModel
from src.gemini import gemini_research
from src.db import get_research_result, init_db
from src.auth import verify_jwt_token, create_jwt_token

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "https://fairy.krz-tech.net").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Fairy API Server"}

from src.users import get_user, create_or_update_tos

@app.post("/api/research")
async def research(body: ResearchBodyModel, token_payload: dict = Depends(verify_jwt_token)):
    user = get_user(body.user_id)
    if not user or not user.tos_agreed:
        raise HTTPException(status_code=403, detail="Terms of Service not agreed")
    
    response = gemini_research(body)
    return response

from pydantic import BaseModel

class TokenRequest(BaseModel):
    user_id: int

@app.post("/api/users/tos")
async def agree_tos(request: TokenRequest, token_payload: dict = Depends(verify_jwt_token)):
    # Verify the user_id in request matches token if needed, or just trust token verification
    # For now, we use the request body user_id but we could validate against token_payload['sub'] if it exists
    user = create_or_update_tos(request.user_id)
    return user

@app.get("/api/research/{uuid}")
async def get_research(uuid: str, token_payload: dict = Depends(verify_jwt_token)):
    result = get_research_result(uuid)
    if result is None:
        raise HTTPException(status_code=404, detail="Research not found")
    if "_id" in result:
        result["_id"] = str(result["_id"])
    return result

@app.post("/api/auth/token")
async def generate_token(request: TokenRequest):
    token = create_jwt_token(request.user_id)
    return {"access_token": token, "token_type": "bearer"}

class MessageIdUpdate(BaseModel):
    message_id: int

from src.db import update_research_message_id

@app.patch("/api/research/{uuid}/message")
async def update_message_id(uuid: str, body: MessageIdUpdate, token_payload: dict = Depends(verify_jwt_token)):
    update_research_message_id(uuid, body.message_id)
    return {"status": "ok"}

class FollowupResearchBody(BaseModel):
    user_id: int
    keyword: str
    parent_message_id: int

from src.db import get_research_by_message_id

@app.post("/api/research/followup")
async def followup_research(body: FollowupResearchBody, token_payload: dict = Depends(verify_jwt_token)):
    user = get_user(body.user_id)
    if not user or not user.tos_agreed:
        raise HTTPException(status_code=403, detail="Terms of Service not agreed")
    
    parent_research = get_research_by_message_id(body.parent_message_id)
    if not parent_research:
        raise HTTPException(status_code=404, detail="Parent research not found")
    
    context = parent_research.get("full_message", "")
    
    # Create a ResearchBodyModel for the new research
    research_body = ResearchBodyModel(user_id=body.user_id, keyword=body.keyword)
    
    response = gemini_research(research_body, context=context)
    return response