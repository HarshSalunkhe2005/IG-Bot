import os
import textwrap
import json
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from backend.core.background_service import get_background

BASE_FONT_PATH = os.path.join("assets", "fonts")
POSTS_DIR = os.path.join("outputs", "posts")
HISTORY_FILE = os.path.join("outputs", "history.json")

STYLE_MAP = {
    "melancholic": os.path.join("Playfair_Display", "static", "PlayfairDisplay-Medium.ttf"),
    "modern": os.path.join("Montserrat", "static", "Montserrat-Regular.ttf"),
    "personal": os.path.join("Caveat", "static", "Caveat-Regular.ttf"),
    "bold": os.path.join("Outfit", "static", "Outfit-Bold.ttf"),
    "minimalist": os.path.join("Inter", "static", "Inter-Regular.ttf")
}

def save_to_history(quote, file_path):
    """Appends the new post data to the history JSON."""
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except:
                history = []
    
    history.append({
        "quote": quote,
        "path": file_path,
        "timestamp": datetime.now().isoformat()
    })
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def create_styled_post(text, vibe="melancholic", bg_type="gradient"):
    width, height = 1080, 1080
    
    # Generate unique filename: post_20260315_0305.png
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"post_{timestamp}.png"
    output_path = os.path.join(POSTS_DIR, filename)

    img = get_background(bg_type=bg_type, width=width, height=height)
    draw = ImageDraw.Draw(img)

    font_rel_path = STYLE_MAP.get(vibe, STYLE_MAP["minimalist"])
    full_font_path = os.path.join(BASE_FONT_PATH, font_rel_path)

    try:
        font = ImageFont.truetype(full_font_path, 70)
    except OSError:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=30)
    line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 30 
    current_y = (height - (len(lines) * line_h)) / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lx = (width - bbox[2]) / 2
        draw.text((lx, current_y), line, fill=(245, 245, 245), font=font)
        current_y += line_h

    # Save the physical file
    img.save(output_path)
    
    # Save to history log
    save_to_history(text, output_path)
    
    return output_path