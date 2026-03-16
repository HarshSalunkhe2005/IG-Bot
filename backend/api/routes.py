from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.core.engine import generate_quote
from backend.core.visualizer import create_styled_post
from backend.core.image_service import generate_background_image # New import

router = APIRouter()

class PostRequest(BaseModel):
    vibe: str = "melancholic"
    text: str = None 
    bg_type: str = "ai_generated" # Defaulting to the new pro feature

@router.post("/draft")
async def draft_quote(request: PostRequest):
    quote = await generate_quote(request.vibe)
    if "Error" in quote:
        raise HTTPException(status_code=500, detail=quote)
    return {"quote": quote, "vibe": request.vibe}

@router.post("/render")
async def render_post(request: PostRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for rendering.")
    
    try:
        # 1. Generate the AI Background based on the text and vibe
        ai_bg_path = None
        if request.bg_type == "ai_generated":
            ai_bg_path = generate_background_image(request.text, vibe=request.vibe)
        
        # 2. Render the post using the new background (or fallback)
        path = create_styled_post(
            request.text, 
            vibe=request.vibe, 
            ai_bg_path=ai_bg_path
        )
        
        return {"message": "Post rendered successfully", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 