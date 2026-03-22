from fastapi import APIRouter, HTTPException
from backend.models.schemas import PostRequest
from backend.core.engine import generate_quote
from backend.core.visualizer import create_styled_post
from backend.core.image_service import generate_background_image

router = APIRouter()

@router.post("/draft")
async def draft_quote(request: PostRequest):
    result = await generate_quote(request.vibe)
    if isinstance(result, tuple):
        quote, font = result
    else:
        raise HTTPException(status_code=500, detail=result)

    if "Error" in quote:
        raise HTTPException(status_code=500, detail=quote)

    return {"quote": quote, "font": font, "vibe": request.vibe}

@router.post("/render")
async def render_post(request: PostRequest):
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required for rendering.")

    try:
        ai_bg_path = None
        if request.bg_type == "ai_generated":
            ai_bg_path = await generate_background_image(
                quote_text=request.text,
                vibe=request.vibe
            )
            if not ai_bg_path:
                print("--- [ROUTE] AI Background generation failed. Falling back. ---")

        path = create_styled_post(
            text=request.text,
            vibe=request.vibe,
            ai_bg_path=ai_bg_path,
            font_name=request.font
        )

        return {"message": "Post rendered successfully", "path": path}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))