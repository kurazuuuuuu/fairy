from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Optional

class ResearchBodyModel(BaseModel):
    user_id: int
    keyword: str

class ResearchResponseModel(BaseModel):
    uuid: UUID4
    owner: int
    smart_message: str = Field(max_length=2000)
    full_message: str
    time: Optional[float]

class HistoryResponseModel(BaseModel):
    user_id: int
    keyword: str
    created_at: datetime

class HistoryResultResponseModel(BaseModel):
    title: str
    content: str