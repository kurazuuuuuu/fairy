import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException

from src.auth import verify_jwt_token
from src.gemini import gemini_research
from src.models import ResearchBodyModel
from src.users import get_user

router = APIRouter()
logger = logging.getLogger("uvicorn")


@router.post("/v2/research")
async def research(body: ResearchBodyModel, token_payload: dict = Depends(verify_jwt_token)):
    user = get_user(body.user_id)
    if not user or not user.tos_agreed:
        raise HTTPException(status_code=403, detail="Terms of Service not agreed")

    logger.info("Executing Google Search Research...")
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, gemini_research, body)
    return response
