import os
import json
from datetime import datetime
from backend.core.reel.ken_burns import make_ken_burns_reel
from backend.core.reel.caption_service import generate_caption, save_caption
from backend.core.image_service import generate_background_image

HISTORY_FILE = os.path.join("outputs", "history.json")


def save_to_history(quote: str, reel_path: str):
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append({
        "quote": quote,
        "path": reel_path,
        "timestamp": datetime.now().isoformat()
    })
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


async def build_reel(quote: str, vibe: str = "melancholic", font_name: str = None,
                     animation: str = "line_fade", short_caption: str = "Reflections") -> dict:
    print(f"--- [REEL BUILDER] Starting | vibe={vibe} | animation={animation} | caption={short_caption} ---")

    image_path = await generate_background_image(quote_text=quote, vibe=vibe)
    if not image_path:
        raise RuntimeError("Background image generation failed. Check UNSPLASH_ACCESS_KEY.")

    try:
        reel_path = make_ken_burns_reel(image_path, quote=quote, font_name=font_name, animation=animation)
    finally:
        # Always clean up temp background regardless of success/failure
        if os.path.exists(image_path):
            os.remove(image_path)

    caption = await generate_caption(short_caption, quote, vibe)
    caption_path = save_caption(caption, reel_path)
    save_to_history(quote, reel_path)

    print(f"--- [REEL BUILDER] Done. Reel: {reel_path} | Caption: {caption_path} ---")

    return {
        "reel_path": reel_path,
        "caption_path": caption_path,
        "caption": caption
    }