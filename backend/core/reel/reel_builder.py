from backend.core.reel.ken_burns import make_ken_burns_reel
from backend.core.reel.caption_service import generate_caption, save_caption

async def build_reel(image_path: str, quote: str, vibe: str = "melancholic", font_name: str = None, animation: str = "line_fade") -> dict:
    print(f"--- [REEL BUILDER] Starting reel build | vibe: {vibe} | animation: {animation} ---")

    reel_path = make_ken_burns_reel(image_path, quote=quote, font_name=font_name, animation=animation)
    caption = await generate_caption(quote, vibe)
    caption_path = save_caption(caption, reel_path)

    print(f"--- [REEL BUILDER] Done. Reel: {reel_path} | Caption: {caption_path} ---")

    return {
        "reel_path": reel_path,
        "caption_path": caption_path,
        "caption": caption
    }