from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Optional, List

class ResearchBodyModel(BaseModel):
    user_id: int
    keyword: str

class UrlMetadata(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None

class UserModel(BaseModel):
    user_id: int
    research_list: list[str]

class ResearchResponseModel(BaseModel):
    uuid: UUID4
    message_id: int
    owner: int
    keyword: str
    smart_message: str = Field(max_length=2000)
    full_message: str
    time: Optional[float]
    urls: List[UrlMetadata] = []
    primary_research_result: UUID4 
    created_at: datetime
    updated_at: datetime