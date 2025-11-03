from fastapi import FastAPI
from src.models import ResearchBodyModel
from src.gemini import gemini_research

api_router = FastAPI()

@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/research")
async def research(body: ResearchBodyModel):
    response = gemini_research(body)
    return response