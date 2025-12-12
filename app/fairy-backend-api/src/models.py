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
    research_list: list[str] = []
    tos_agreed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ResearchResponseModel(BaseModel):
    uuid: UUID4
    message_id: int
    owner: int
    keyword: str
    smart_message: str = Field(max_length=1000)
    full_message: str
    time: Optional[float] = None
    urls: List[UrlMetadata] = []
    urls_excluded_count: int = 0
    primary_research_result: Optional[UUID4] = None
    total_tokens: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)