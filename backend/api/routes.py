from fastapi import APIRouter, HTTPException
from backend.models.schemas import PostRequest, ShortRequest, PostToYoutubeRequest, RetryFailedPostRequest
from backend.core.engine import generate_quote
from backend.core.visualizer import create_styled_post
from backend.core.image_service import generate_background_image
from backend.core.reel.reel_builder import build_reel
from backend.core.youtube_service import post_short_to_youtube, load_failed_posts, remove_failed_post, increment_retry_count

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
                quote_text=request.text, vibe=request.vibe
            )
            if not ai_bg_path:
                print("--- [ROUTE] AI Background generation failed. Falling back. ---")

        post_path, clean_bg_path = create_styled_post(
            text=request.text, vibe=request.vibe,
            ai_bg_path=ai_bg_path, font_name=request.font
        )
        return {
            "message": "Post rendered successfully",
            "path": post_path,
            "clean_bg_path": clean_bg_path,
            "font": request.font
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/short")
async def render_short(request: ShortRequest):
    try:
        result = await build_reel(
            image_path=request.image_path,
            quote=request.quote,
            vibe=request.vibe,
            font_name=request.font
        )
        return {
            "message": "Short built successfully",
            "reel_path": result["reel_path"],
            "caption_path": result["caption_path"],
            "caption": result["caption"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/post-to-youtube")
async def post_to_youtube(request: PostToYoutubeRequest):
    """Post short to YouTube"""
    result = await post_short_to_youtube(request.reel_path, request.caption)

    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail={
                "error": result.get("error"),
                "suggestion": result.get("suggestion")
            }
        )

    return {
        "success": True,
        "post_url": result.get("post_url"),
        "post_id": result.get("post_id"),
        "message": result.get("message")
    }

@router.post("/retry-failed-post")
async def retry_failed_post(request: RetryFailedPostRequest):
    """Retry posting a failed short"""
    increment_retry_count(request.reel_path)
    result = await post_short_to_youtube(request.reel_path, request.caption)

    if result.get("success"):
        remove_failed_post(request.reel_path)
        return {
            "success": True,
            "post_url": result.get("post_url"),
            "post_id": result.get("post_id"),
            "message": "Short posted successfully on retry!"
        }
    else:
        raise HTTPException(
            status_code=500,
            detail={
                "error": result.get("error"),
                "suggestion": result.get("suggestion")
            }
        )

@router.get("/failed-posts")
async def get_failed_posts():
    """Get list of failed posts for user"""
    failed_posts = load_failed_posts()
    return {"failed_posts": failed_posts, "count": len(failed_posts)}