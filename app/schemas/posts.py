from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class PostBaseV1(BaseModel):
    username: str
    title: str
    content: str
    image: Optional[list] = None

class PostInDBV1(PostBaseV1):
    created_at: datetime

class PostCreateV1(PostBaseV1):
    pass

class LikeCreate(BaseModel):
    user_id: UUID
    post_title: str

class PostUpdateV1(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class Response(BaseModel):
    message: str
    data: Optional[dict | list[dict] | list] = None
