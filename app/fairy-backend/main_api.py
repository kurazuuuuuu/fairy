from fastapi import FastAPI
from src.models import ResearchBodyModel
from src.gemini import gemini_research

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Fairy API Server"}

@app.post("/api/research")
async def research(body: ResearchBodyModel):
    response = gemini_research(body)
    return response