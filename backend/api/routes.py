from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.engine import generate_quote
from core.visualizer import create_styled_post

router = APIRouter()

# Schema for incoming requests
class PostRequest(BaseModel):
    vibe: str = "melancholic"
    text: str = None  # Optional: allows manual override

@router.post("/draft")
async def draft_quote(request: PostRequest):
    """Generates the text draft for user review."""
    quote = await generate_quote(request.vibe)
    if "Error" in quote:
        raise HTTPException(status_code=500, detail=quote)
    return {"quote": quote, "vibe": request.vibe}

@router.post("/render")
async def render_post(request: PostRequest):
    """Converts confirmed text into the final image."""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for rendering.")
    
    try:
        path = create_styled_post(request.text, vibe=request.vibe)
        return {"message": "Post rendered successfully", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))