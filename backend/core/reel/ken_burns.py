import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import httpx
import io
import re
import textwrap
import os
from moviepy.editor import VideoClip

REELS_DIR = os.path.join("outputs", "reels")
os.makedirs(REELS_DIR, exist_ok=True)

DEFAULT_FONT = "Playfair Display"

def fetch_google_font_pil(font_name: str, size: int = 60) -> ImageFont.FreeTypeFont:
    """Fetches a Google Font and returns PIL ImageFont."""
    try:
        css_url = f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}:wght@400;700"
        headers = {"User-Agent": "Mozilla/5.0"}
        with httpx.Client(timeout=30.0) as client:
            css_resp = client.get(css_url, headers=headers)
            urls = re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+\.ttf)\)', css_resp.text)
            if not urls:
                raise Exception("No TTF found")
            font_resp = client.get(urls[0], headers=headers)
            return ImageFont.truetype(io.BytesIO(font_resp.content), size)
    except Exception as e:
        print(f"--- [KEN BURNS] Font fetch failed ({e}). Using default. ---")
        return ImageFont.load_default()

def make_ken_burns_reel(image_path: str, quote: str, font_name: str = None, duration: int = 12, fps: int = 30) -> str:
    """
    Ken Burns zoom + line-by-line fade-in text overlay.
    Each line fades in sequentially. Fully burned into the .mp4.
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    # Font
    selected_font = font_name if font_name else DEFAULT_FONT
    font = fetch_google_font_pil(selected_font, size=62)

    # Wrap text into lines
    lines = textwrap.wrap(quote, width=26)
    total_lines = len(lines)

    # Timing: each line gets equal share of duration
    # First 20% = no text (just zoom), then lines fade in one by one
    intro_end = duration * 0.15
    time_per_line = (duration - intro_end) / total_lines

    # Ken Burns: zoom from 100% to 115%
    start_scale = 1.0
    end_scale = 1.15

    def make_frame(t):
        progress = t / duration
        scale = start_scale + (end_scale - start_scale) * progress

        new_w = int(w * scale)
        new_h = int(h * scale)

        zoomed = Image.fromarray(img_array).resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        frame = zoomed.crop((left, top, left + w, top + h)).convert("RGBA")

        draw = ImageDraw.Draw(frame)

        # Calculate vertical center for all lines
        line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 36
        total_text_h = total_lines * line_h
        start_y = (h - total_text_h) / 2

        for i, line in enumerate(lines):
            # When does this line start fading in?
            line_start = intro_end + (i * time_per_line)
            line_fade_duration = time_per_line * 0.6  # fade over 60% of its slot

            if t < line_start:
                alpha = 0
            elif t < line_start + line_fade_duration:
                alpha = int(255 * ((t - line_start) / line_fade_duration))
            else:
                alpha = 255

            if alpha <= 0:
                continue

            bbox = draw.textbbox((0, 0), line, font=font)
            lx = (w - (bbox[2] - bbox[0])) / 2
            ly = start_y + (i * line_h)

            # Shadow for readability
            shadow_color = (0, 0, 0, min(alpha, 180))
            draw.text((lx + 2, ly + 2), line, font=font, fill=shadow_color)

            # Main text
            text_color = (255, 255, 255, alpha)
            draw.text((lx, ly), line, font=font, fill=text_color)

        return np.array(frame.convert("RGB"))

    clip = VideoClip(make_frame, duration=duration)
    clip = clip.set_fps(fps)

    output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_reel.mp4"
    output_path = os.path.join(REELS_DIR, output_filename)

    clip.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio=False,
        logger=None
    )

    print(f"--- [KEN BURNS] Reel saved: {output_path} ---")
    return output_path