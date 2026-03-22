import os
import io
import textwrap
import json
import httpx
import re
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

POSTS_DIR = os.path.join("outputs", "posts")
HISTORY_FILE = os.path.join("outputs", "history.json")
os.makedirs(POSTS_DIR, exist_ok=True)

DEFAULT_FONT = "Playfair Display"
PADDING = 120

def save_to_history(quote, file_path):
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

def fetch_google_font(font_name: str, size: int = 68) -> ImageFont.FreeTypeFont:
    try:
        css_url = f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}:wght@400;700"
        headers = {"User-Agent": "Mozilla/5.0"}

        with httpx.Client(timeout=30.0) as client:
            css_resp = client.get(css_url, headers=headers)
            if css_resp.status_code != 200:
                raise Exception(f"CSS fetch failed: {css_resp.status_code}")

            urls = re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+\.ttf)\)', css_resp.text)
            if not urls:
                raise Exception("No TTF URL found")

            font_resp = client.get(urls[0], headers=headers)
            if font_resp.status_code != 200:
                raise Exception(f"Font file fetch failed: {font_resp.status_code}")

            return ImageFont.truetype(io.BytesIO(font_resp.content), size)

    except Exception as e:
        print(f"--- [VISUALIZER] Font fetch failed ({e}). Using default. ---")
        return ImageFont.load_default()

def process_ai_background(image_path, width=1080, height=1080):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((width, height), Image.Resampling.LANCZOS)
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    img = ImageEnhance.Brightness(img).enhance(0.5)
    img = ImageEnhance.Contrast(img).enhance(1.2)
    return img

def create_styled_post(text, vibe="melancholic", ai_bg_path=None, font_name=None):
    width, height = 1080, 1080
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(POSTS_DIR, f"post_{timestamp}.png")
    clean_bg_path = os.path.join(POSTS_DIR, f"post_{timestamp}_bg.png")

    # Build background
    if ai_bg_path and os.path.exists(ai_bg_path):
        img = process_ai_background(ai_bg_path)
    else:
        img = Image.new("RGB", (width, height), (15, 15, 15))

    # Save clean background for reel (no text)
    img.save(clean_bg_path)
    print(f"--- [VISUALIZER] Clean BG saved: {clean_bg_path} ---")

    # Now render text on top for the static post
    draw = ImageDraw.Draw(img)
    selected_font = font_name if font_name else DEFAULT_FONT
    print(f"--- [VISUALIZER] Using font: {selected_font} ---")

    max_text_width = width - (PADDING * 2)
    font_size = 72
    font = fetch_google_font(selected_font, font_size)

    while font_size > 32:
        font = fetch_google_font(selected_font, font_size)
        lines = textwrap.wrap(text, width=26)
        max_line_width = max(
            draw.textbbox((0, 0), line, font=font)[2] for line in lines
        )
        if max_line_width <= max_text_width:
            break
        font_size -= 4

    lines = textwrap.wrap(text, width=26)
    line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 36
    total_text_height = len(lines) * line_h
    current_y = (height - total_text_height) / 2

    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lx = (width - (bbox[2] - bbox[0])) / 2
        draw.text((lx, current_y), line, fill=(255, 255, 255), font=font)
        current_y += line_h

    img.save(output_path)
    save_to_history(text, output_path)

    # Cleanup temp AI background
    if ai_bg_path and os.path.exists(ai_bg_path):
        os.remove(ai_bg_path)

    return output_path, clean_bg_path