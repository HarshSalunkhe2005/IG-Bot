import numpy as np
from PIL import Image, ImageDraw, ImageFont
import httpx
import io
import re
import textwrap
import os
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REELS_DIR = os.path.join("outputs", "reels")
os.makedirs(REELS_DIR, exist_ok=True)

DEFAULT_FONT = "Playfair Display"

def fetch_google_font_pil(font_name: str, size: int = 60) -> ImageFont.FreeTypeFont:
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
        logger.warning(f"[KEN BURNS] Font fetch failed ({e}). Using default.")
        return ImageFont.load_default()

def make_ken_burns_reel(image_path: str, quote: str, font_name: str = None, animation: str = "line_fade", fps: int = 30) -> str:
    img = Image.open(image_path).convert("RGB")
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    selected_font = font_name if font_name else DEFAULT_FONT
    font = fetch_google_font_pil(selected_font, size=62)

    lines = textwrap.wrap(quote, width=26)
    total_lines = len(lines)

    # Dynamic duration: 2.5s per line minimum, 6s intro+outro buffer
    duration = max(12, total_lines * 2.5 + 6)

    # Ken Burns zoom range
    start_scale = 1.0
    end_scale = 1.15

    intro_end = duration * 0.15
    time_per_line = (duration - intro_end) / total_lines

    def get_alpha(t, i):
        """Returns alpha 0-255 for line i at time t."""
        line_start = intro_end + (i * time_per_line)
        fade_dur = time_per_line * 0.6
        if t < line_start:
            return 0
        elif t < line_start + fade_dur:
            return int(255 * ((t - line_start) / fade_dur))
        return 255

    def get_word_alpha(t, word_index, total_words):
        """Word by word alpha."""
        time_per_word = (duration - intro_end) / total_words
        word_start = intro_end + (word_index * time_per_word)
        fade_dur = time_per_word * 0.5
        if t < word_start:
            return 0
        elif t < word_start + fade_dur:
            return int(255 * ((t - word_start) / fade_dur))
        return 255

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

        line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 36
        total_text_h = total_lines * line_h
        start_y = (h - total_text_h) / 2

        if animation == "word_fade":
            all_words = quote.split()
            total_words = len(all_words)
            word_idx = 0
            for i, line in enumerate(lines):
                words = line.split()
                line_bbox = draw.textbbox((0, 0), line, font=font)
                lx = (w - (line_bbox[2] - line_bbox[0])) / 2
                ly = start_y + (i * line_h)
                cx = lx
                for word in words:
                    alpha = get_word_alpha(t, word_idx, total_words)
                    if alpha > 0:
                        draw.text((cx + 2, ly + 2), word, font=font, fill=(0, 0, 0, min(alpha, 180)))
                        draw.text((cx, ly), word, font=font, fill=(255, 255, 255, alpha))
                    word_bbox = draw.textbbox((0, 0), word + " ", font=font)
                    cx += word_bbox[2] - word_bbox[0]
                    word_idx += 1

        elif animation == "typewriter":
            for i, line in enumerate(lines):
                line_start = intro_end + (i * time_per_line)
                if t < line_start:
                    continue
                elapsed = t - line_start
                chars_per_sec = len(line) / time_per_line
                chars_shown = int(elapsed * chars_per_sec)
                partial = line[:chars_shown]
                bbox = draw.textbbox((0, 0), line, font=font)
                lx = (w - (bbox[2] - bbox[0])) / 2
                ly = start_y + (i * line_h)
                draw.text((lx + 2, ly + 2), partial, font=font, fill=(0, 0, 0, 180))
                draw.text((lx, ly), partial, font=font, fill=(255, 255, 255, 255))

        elif animation == "slide_up":
            for i, line in enumerate(lines):
                alpha = get_alpha(t, i)
                if alpha <= 0:
                    continue
                line_start = intro_end + (i * time_per_line)
                fade_dur = time_per_line * 0.6
                elapsed = max(0, t - line_start)
                progress_line = min(1.0, elapsed / fade_dur)
                offset = int(30 * (1 - progress_line))
                bbox = draw.textbbox((0, 0), line, font=font)
                lx = (w - (bbox[2] - bbox[0])) / 2
                ly = start_y + (i * line_h) + offset
                draw.text((lx + 2, ly + 2), line, font=font, fill=(0, 0, 0, min(alpha, 180)))
                draw.text((lx, ly), line, font=font, fill=(255, 255, 255, alpha))

        elif animation == "zoom_in":
            for i, line in enumerate(lines):
                alpha = get_alpha(t, i)
                if alpha <= 0:
                    continue
                line_start = intro_end + (i * time_per_line)
                fade_dur = time_per_line * 0.6
                elapsed = max(0, t - line_start)
                scale_progress = min(1.0, elapsed / fade_dur)
                scale_factor = 0.7 + (0.3 * scale_progress)
                scaled_size = max(20, int(62 * scale_factor))
                scaled_font = fetch_google_font_pil(selected_font, size=scaled_size)
                bbox = draw.textbbox((0, 0), line, font=scaled_font)
                lx = (w - (bbox[2] - bbox[0])) / 2
                ly = start_y + (i * line_h)
                draw.text((lx + 2, ly + 2), line, font=scaled_font, fill=(0, 0, 0, min(alpha, 180)))
                draw.text((lx, ly), line, font=scaled_font, fill=(255, 255, 255, alpha))

        else:  # line_fade (default)
            for i, line in enumerate(lines):
                alpha = get_alpha(t, i)
                if alpha <= 0:
                    continue
                bbox = draw.textbbox((0, 0), line, font=font)
                lx = (w - (bbox[2] - bbox[0])) / 2
                ly = start_y + (i * line_h)
                draw.text((lx + 2, ly + 2), line, font=font, fill=(0, 0, 0, min(alpha, 180)))
                draw.text((lx, ly), line, font=font, fill=(255, 255, 255, alpha))

        return np.array(frame.convert("RGB"))

    clip = VideoClip(make_frame, duration=duration)
    clip = clip.set_fps(fps)

    # Add silent audio track (will upgrade with bg music later)
    silent_audio = CompositeAudioClip([])
    clip = clip.set_audio(silent_audio)

    output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_reel.mp4"
    output_path = os.path.join(REELS_DIR, output_filename)

    logger.info(f"[KEN BURNS] Creating reel with duration {duration}s...")
    clip.write_videofile(output_path, fps=fps, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    logger.info(f"[KEN BURNS] Reel saved: {output_path}")
    return output_path