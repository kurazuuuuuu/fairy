from fastapi import APIRouter, HTTPException, Depends
from src.models import ResearchBodyModel
from src.auth import verify_jwt_token
from src.users import get_user
from src.gemini import gemini_research, rag_research
from src.services.redis_manager import redis_manager
from src.ollama_client import get_embedding, extract_keywords_from_ollama
from src.db import save_research_result
from src.users import add_research_to_user
from src.models import ResearchResponseModel, UrlMetadata
import logging
import uuid
import time
from datetime import datetime
import asyncio

router = APIRouter()
logger = logging.getLogger("uvicorn")

@router.post("/v2/research")
async def research(body: ResearchBodyModel, token_payload: dict = Depends(verify_jwt_token)):
    user = get_user(body.user_id)
    if not user or not user.tos_agreed:
        raise HTTPException(status_code=403, detail="Terms of Service not agreed")

    # 1. Exact Match Cache Check
    cached_result = await redis_manager.get_cache(body.keyword)
    if cached_result:
        logger.info(f"Returning cached result for: {body.keyword}")
        # Convert dict back to model if needed, but returning dict is fine for FastAPI
        return cached_result

    # 2. Vector Search (RAG) Check
    # Extract keywords for embedding (remove noise)
    extracted_keyword = extract_keywords_from_ollama(body.keyword)
    embedding = get_embedding(extracted_keyword)
    
    sim_results = []
    if embedding:
        sim_results = await redis_manager.vector_search(embedding, top_k=3, threshold=0.25)
    
    rag_context = ""
    if sim_results:
        logger.info(f"Vector search hit: {len(sim_results)} results")
        # Construct context from top results
        for res in sim_results:
            rag_context += f"## 過去レポート: {res['keyword']}\n{res['full_message']}\n\n"
        
        # Try RAG generation
        try:
            logger.info("Executing RAG-based Research...")
            loop = asyncio.get_event_loop()
            response_model = await loop.run_in_executor(None, rag_research, body, rag_context)
            
            # Save to Redis (Update cache with this specific question)
            await redis_manager.save_research(body.keyword, response_model.model_dump(mode='json'), embedding)
            
            return response_model
            
        except Exception as e:
            logger.warning(f"RAG generation failed, falling back to full research: {e}")
            # Fallback to normal research
            pass

    # 3. Full Research (Fallback or No Hit)
    logger.info("Executing Full Google Search Research...")
    loop = asyncio.get_event_loop()
    # gemini_research saves to DB internally
    response = await loop.run_in_executor(None, gemini_research, body)
    
    # 4. Save to Redis with Embedding
    if embedding:
        await redis_manager.save_research(body.keyword, response.model_dump(mode='json'), embedding)
    
    return response
