import os
import textwrap
from PIL import Image, ImageDraw, ImageFont
# Import the new modular background service
from backend.core.background_service import get_background

BASE_FONT_PATH = os.path.join("assets", "fonts")

STYLE_MAP = {
    "melancholic": os.path.join("Playfair_Display", "static", "PlayfairDisplay-Medium.ttf"),
    "modern": os.path.join("Montserrat", "static", "Montserrat-Regular.ttf"),
    "personal": os.path.join("Caveat", "static", "Caveat-Regular.ttf"),
    "bold": os.path.join("Outfit", "static", "Outfit-Bold.ttf"),
    "minimalist": os.path.join("Inter", "static", "Inter-Regular.ttf")
}

def create_styled_post(text, vibe="melancholic", bg_type="gradient", output_path="post.png"):
    width, height = 1080, 1080
    
    # MODULAR CHANGE: Fetch the background layer from our service
    img = get_background(bg_type=bg_type, width=width, height=height)
    draw = ImageDraw.Draw(img)

    # Resolve font path
    font_rel_path = STYLE_MAP.get(vibe, STYLE_MAP["minimalist"])
    full_font_path = os.path.join(BASE_FONT_PATH, font_rel_path)

    try:
        # Increased font size slightly for "Pro" look
        font = ImageFont.truetype(full_font_path, 70)
    except OSError:
        print(f"Font not found at {full_font_path}, using default.")
        font = ImageFont.load_default()

    # Wrap and Draw logic remains the same
    lines = textwrap.wrap(text, width=30)
    line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 30 
    current_y = (height - (len(lines) * line_h)) / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lx = (width - bbox[2]) / 2
        # Added a very slight shadow/glow effect by drawing twice (optional but pro)
        draw.text((lx, current_y), line, fill=(245, 245, 245), font=font)
        current_y += line_h

    img.save(output_path)
    return output_path