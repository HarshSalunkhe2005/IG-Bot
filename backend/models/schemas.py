from pydantic import BaseModel
from typing import Optional

class PostRequest(BaseModel):
    vibe: str = "melancholic"
    text: Optional[str] = None
    bg_type: str = "ai_generated"
    font: Optional[str] = None

class ShortRequest(BaseModel):
    quote: str
    vibe: str = "melancholic"
    font: Optional[str] = None
    animation: str = "line_fade"
    caption: str = "Reflections"

class PostToYoutubeRequest(BaseModel):
    reel_path: str
    caption: str

class RetryFailedPostRequest(BaseModel):
    reel_path: str
    caption: str