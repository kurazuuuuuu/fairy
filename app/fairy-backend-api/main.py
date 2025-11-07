import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.models import ResearchBodyModel
from src.gemini import gemini_research
from src.db import get_research_result
from src.auth import verify_jwt_token, create_jwt_token

app = FastAPI()

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

@app.post("/api/research")
async def research(body: ResearchBodyModel, token_payload: dict = Depends(verify_jwt_token)):
    response = gemini_research(body)
    return response

@app.get("/api/research/{uuid}")
async def get_research(uuid: str, token_payload: dict = Depends(verify_jwt_token)):
    result = get_research_result(uuid)
    if result is None:
        raise HTTPException(status_code=404, detail="Research not found")
    if "_id" in result:
        result["_id"] = str(result["_id"])
    return result

from pydantic import BaseModel

class TokenRequest(BaseModel):
    user_id: int

@app.post("/api/auth/token")
async def generate_token(request: TokenRequest):
    token = create_jwt_token(request.user_id)
    return {"access_token": token, "token_type": "bearer"}