import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.models import ResearchBodyModel
from src.gemini import gemini_research
from src.db import get_research_result

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
async def research(body: ResearchBodyModel):
    response = gemini_research(body)
    return response

@app.get("/api/research/{uuid}")
async def get_research(uuid: str):
    result = get_research_result(uuid)
    if result is None:
        raise HTTPException(status_code=404, detail="Research not found")
    if "_id" in result:
        result["_id"] = str(result["_id"])
    return result