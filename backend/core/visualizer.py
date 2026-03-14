import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Define absolute path to fonts based on your hierarchy
BASE_FONT_PATH = os.path.join("assets", "fonts")

# Map vibes to your downloaded fonts
STYLE_MAP = {
    "melancholic": os.path.join("Playfair_Display", "static", "PlayfairDisplay-Medium.ttf"),
    "modern": os.path.join("Montserrat", "static", "Montserrat-Regular.ttf"),
    "personal": os.path.join("Caveat", "static", "Caveat-Regular.ttf"),
    "bold": os.path.join("Outfit", "static", "Outfit-Bold.ttf"),
    "minimalist": os.path.join("Inter", "static", "Inter-Regular.ttf")
}

def create_styled_post(text, vibe="melancholic", output_path="post.png"):
    width, height = 1080, 1080
    img = Image.new("RGB", (width, height), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)

    # Resolve font path
    font_rel_path = STYLE_MAP.get(vibe, STYLE_MAP["minimalist"])
    full_font_path = os.path.join(BASE_FONT_PATH, font_rel_path)

    try:
        font = ImageFont.truetype(full_font_path, 65)
    except OSError:
        print(f"Font not found at {full_font_path}, using default.")
        font = ImageFont.load_default()

    # Wrap and Draw
    lines = textwrap.wrap(text, width=30)
    line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 25
    current_y = (height - (len(lines) * line_h)) / 2

    for line in lines:
        lx = (width - draw.textbbox((0, 0), line, font=font)[2]) / 2
        draw.text((lx, current_y), line, fill=(240, 240, 240), font=font)
        current_y += line_h

    img.save(output_path)
    return output_path