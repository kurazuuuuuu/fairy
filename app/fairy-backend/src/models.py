from pydantic import BaseModel
from datetime import datetime

class ResearchBodyModel(BaseModel):
    user_id: str
    keyword: str

class ResearchResponseModel(BaseModel):
    uuid: str
    message: str

class HistoryResponseModel(BaseModel):
    user_id: str
    keyword: str
    created_at: datetime

class HistoryResultResponseModel(BaseModel):
    title: str
    content: str