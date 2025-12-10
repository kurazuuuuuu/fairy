from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.models import ResearchBodyModel
from src.gemini import gemini_research
from src.db import get_research_result, init_db, update_research_message_id, get_research_by_message_id
from src.auth import verify_jwt_token, create_jwt_token
from src.ogp import generate_ogp_image, generate_ogp_html
from src.users import get_user, create_or_update_tos
from src.config import config

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    config.validate()
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Fairy API Server"}



@app.post("/v2/research")
async def research(body: ResearchBodyModel, token_payload: dict = Depends(verify_jwt_token)):
    user = get_user(body.user_id)
    if not user or not user.tos_agreed:
        raise HTTPException(status_code=403, detail="Terms of Service not agreed")
    
    response = gemini_research(body)
    return response



class TokenRequest(BaseModel):
    user_id: int

@app.post("/v2/users/tos")
async def agree_tos(request: TokenRequest, token_payload: dict = Depends(verify_jwt_token)):
    # Verify the user_id in request matches token if needed, or just trust token verification
    # For now, we use the request body user_id but we could validate against token_payload['sub'] if it exists
    user = create_or_update_tos(request.user_id)
    return user

@app.get("/v2/research/{uuid}")
async def get_research(uuid: str, token_payload: dict = Depends(verify_jwt_token)):
    result = get_research_result(uuid)
    if result is None:
        raise HTTPException(status_code=404, detail="Research not found")
    if "_id" in result:
        result["_id"] = str(result["_id"])
    return result

@app.post("/v2/auth/token")
async def generate_token(request: TokenRequest):
    token = create_jwt_token(request.user_id)
    return {"access_token": token, "token_type": "bearer"}

class MessageIdUpdate(BaseModel):
    message_id: int


@app.patch("/v2/research/{uuid}/message")
async def update_message_id(uuid: str, body: MessageIdUpdate, token_payload: dict = Depends(verify_jwt_token)):
    update_research_message_id(uuid, body.message_id)
    return {"status": "ok"}

class FollowupResearchBody(BaseModel):
    user_id: int
    keyword: str
    parent_message_id: int


@app.post("/v2/research/followup")
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

# OGP endpoints (no authentication required for social media crawlers)
# OGPエンドポイント（SNSクローラー向け、認証不要）

@app.get("/v2/research/{uuid}/ogp.png")
async def get_research_ogp_image(uuid: str):
    """
    Generate and return OGP image for research result.
    リサーチ結果のOGP画像を生成して返す。
    """
    result = get_research_result(uuid)
    if result is None:
        raise HTTPException(status_code=404, detail="Research not found")
    
    keyword = result.get("keyword", "")
    # Use smart_message for body text, fallback to full_message
    body_text = result.get("smart_message", result.get("full_message", ""))
    
    # Generate OGP image
    image_bytes = generate_ogp_image(keyword, body_text)
    
    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
        }
    )

@app.get("/v2/research/{uuid}/ogp")
async def get_research_ogp_html(uuid: str):
    """
    Return HTML page with OGP meta tags for social media crawlers.
    SNSクローラー向けにOGPメタタグを含むHTMLを返す。
    """
    result = get_research_result(uuid)
    if result is None:
        raise HTTPException(status_code=404, detail="Research not found")
    
    keyword = result.get("keyword", "")
    smart_message = result.get("smart_message", "")
    
    # Get base URLs from config
    base_url = config.BASE_URL
    frontend_url = config.FRONTEND_URL
    
    html = generate_ogp_html(
        uuid=uuid,
        keyword=keyword,
        smart_message=smart_message,
        base_url=base_url,
        frontend_url=frontend_url,
    )
    
    return HTMLResponse(content=html)