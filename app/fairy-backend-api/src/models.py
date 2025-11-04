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

class ResearchResponseModel(BaseModel):
    uuid: UUID4
    owner: int
    smart_message: str = Field(max_length=2000)
    full_message: str
    time: Optional[float]