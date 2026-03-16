import os
import textwrap
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

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
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try: history = json.load(f)
            except: history = []
    
    history.append({
        "quote": quote,
        "path": file_path,
        "timestamp": datetime.now().isoformat()
    })
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def process_ai_background(image_path, width=1080, height=1080):
    """Applies pro filters to the AI-generated raw image."""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Apply our "Pro Look" formula
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    img = ImageEnhance.Brightness(img).enhance(0.5) # Slightly darker for AI images
    img = ImageEnhance.Contrast(img).enhance(1.2)
    
    return img

def create_styled_post(text, vibe="melancholic", ai_bg_path=None):
    width, height = 1080, 1080
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(POSTS_DIR, f"post_{timestamp}.png")

    # Use AI background if provided, otherwise fallback to a dark neutral
    if ai_bg_path and os.path.exists(ai_bg_path):
        img = process_ai_background(ai_bg_path)
    else:
        img = Image.new("RGB", (width, height), (15, 15, 15))

    draw = ImageDraw.Draw(img)
    font_rel_path = STYLE_MAP.get(vibe, STYLE_MAP["minimalist"])
    full_font_path = os.path.join(BASE_FONT_PATH, font_rel_path)

    try:
        font = ImageFont.truetype(full_font_path, 75)
    except:
        font = ImageFont.load_default()

    lines = textwrap.wrap(text, width=28)
    line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 40
    current_y = (height - (len(lines) * line_h)) / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lx = (width - (bbox[2] - bbox[0])) / 2
        draw.text((lx, current_y), line, fill=(255, 255, 255), font=font)
        current_y += line_h

    img.save(output_path)
    save_to_history(text, output_path)
    
    # Cleanup: Remove the temporary raw AI image
    if ai_bg_path and os.path.exists(ai_bg_path):
        os.remove(ai_bg_path)

    return output_path