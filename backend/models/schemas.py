from pydantic import BaseModel
from typing import Optional

class PostRequest(BaseModel):
    vibe: str = "melancholic"
    text: Optional[str] = None
    bg_type: str = "ai_generated"
    font: Optional[str] = None

class ReelRequest(BaseModel):
    image_path: str
    quote: str
    vibe: str = "melancholic"
    font: Optional[str] = None

class PostToInstagramRequest(BaseModel):
    reel_path: str
    caption: str

class RetryFailedPostRequest(BaseModel):
    reel_path: str
    caption: str