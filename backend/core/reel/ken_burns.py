import numpy as np
from PIL import Image, ImageDraw, ImageFont
import httpx
import io
import re
import textwrap
import os
from moviepy.editor import VideoClip
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REELS_DIR = os.path.join("outputs", "reels")
os.makedirs(REELS_DIR, exist_ok=True)

DEFAULT_FONT = "Playfair Display"
BASE_FONT_SIZE = 62
INTRO_DUR = 1.5   # seconds of background before any text
OUTRO_DUR = 2.0   # seconds to hold after all text is visible

# Per-animation timing constants
TYPEWRITER_MS_PER_CHAR = 0.05    # 50ms per character
WORD_FADE_MS_PER_WORD = 0.20     # 200ms per word
WORD_FADE_FADE_DUR = 0.15        # 150ms to fully fade in each word
LINE_FADE_MS_PER_LINE = 0.40     # 400ms per line
LINE_FADE_FADE_DUR = 0.30        # 300ms to fully fade in each line
SLIDE_UP_MS_PER_WORD = 0.28      # 280ms per word
SLIDE_UP_FADE_DUR = 0.22         # 220ms per word animation
ZOOM_IN_MS_PER_WORD = 0.32       # 320ms per word
ZOOM_IN_FADE_DUR = 0.25          # 250ms per word animation

# Module-level font bytes cache: font_name -> raw bytes
_font_bytes_cache: dict = {}


def fetch_google_font_pil(font_name: str, size: int = BASE_FONT_SIZE) -> ImageFont.FreeTypeFont:
    """Download font once, then create PIL fonts at any size from cached bytes."""
    try:
        if font_name not in _font_bytes_cache:
            css_url = f"https://fonts.googleapis.com/css2?family={font_name.replace(' ', '+')}:wght@400;700"
            headers = {"User-Agent": "Mozilla/5.0"}
            with httpx.Client(timeout=30.0) as client:
                css_resp = client.get(css_url, headers=headers)
                urls = re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+\.ttf)\)', css_resp.text)
                if not urls:
                    raise Exception("No TTF found")
                font_resp = client.get(urls[0], headers=headers)
                _font_bytes_cache[font_name] = font_resp.content
        return ImageFont.truetype(io.BytesIO(_font_bytes_cache[font_name]), size)
    except Exception as e:
        logger.warning(f"[KEN BURNS] Font fetch failed ({e}). Using default.")
        return ImageFont.load_default()


def _compute_duration(animation: str, lines: list, quote: str) -> float:
    """Compute video duration based on animation type and content length."""
    total_words = len(quote.split())
    total_chars = sum(len(line) for line in lines)
    total_lines = len(lines)

    if animation == "typewriter":
        text_dur = total_chars * TYPEWRITER_MS_PER_CHAR
    elif animation == "word_fade":
        text_dur = total_words * WORD_FADE_MS_PER_WORD + WORD_FADE_FADE_DUR
    elif animation == "slide_up":
        text_dur = total_words * SLIDE_UP_MS_PER_WORD + SLIDE_UP_FADE_DUR
    elif animation == "zoom_in":
        text_dur = total_words * ZOOM_IN_MS_PER_WORD + ZOOM_IN_FADE_DUR
    else:  # line_fade
        text_dur = total_lines * LINE_FADE_MS_PER_LINE + LINE_FADE_FADE_DUR

    return max(8.0, INTRO_DUR + text_dur + OUTRO_DUR)


def _compute_word_positions(lines: list, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont,
                             w: int, start_y: float, line_h: float) -> list:
    """Pre-compute (word, cx, ly) for every word across all lines."""
    positions = []
    for i, line in enumerate(lines):
        words = line.split()
        line_bbox = draw.textbbox((0, 0), line, font=font)
        lx = (w - (line_bbox[2] - line_bbox[0])) / 2
        cx = lx
        ly = start_y + i * line_h
        for word in words:
            positions.append((word, cx, ly))
            wb = draw.textbbox((0, 0), word + " ", font=font)
            cx += wb[2] - wb[0]
    return positions


def make_ken_burns_reel(image_path: str, quote: str, font_name: str = None,
                        animation: str = "line_fade", fps: int = 30) -> str:
    img = Image.open(image_path).convert("RGB")
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
    img_array = np.array(img)
    h, w = img_array.shape[:2]

    selected_font = font_name if font_name else DEFAULT_FONT
    font = fetch_google_font_pil(selected_font, size=BASE_FONT_SIZE)

    lines = textwrap.wrap(quote, width=26)
    total_lines = len(lines)
    duration = _compute_duration(animation, lines, quote)

    # Ken Burns zoom
    start_scale = 1.0
    end_scale = 1.15

    # Pre-compute a temp draw surface to measure text positions (font metrics only)
    _tmp_img = Image.new("RGBA", (w, h))
    _tmp_draw = ImageDraw.Draw(_tmp_img)
    line_h = font.getbbox("hg")[3] - font.getbbox("hg")[1] + 36
    total_text_h = total_lines * line_h
    start_y = (h - total_text_h) / 2

    # Pre-compute word positions (used by word-level animations)
    word_positions = _compute_word_positions(lines, _tmp_draw, font, w, start_y, line_h)

    # Pre-compute zoom fonts (for zoom_in animation) — only one download needed
    zoom_font_lookup: dict = {}
    if animation == "zoom_in":
        for pct in range(50, 105, 5):
            size = max(20, int(BASE_FONT_SIZE * pct / 100))
            zoom_font_lookup[pct] = fetch_google_font_pil(selected_font, size=size)

    def _get_zoom_font(progress_w: float) -> ImageFont.FreeTypeFont:
        """Return closest pre-cached font for given animation progress (0-1)."""
        scale = 0.5 + 0.5 * progress_w  # 50% → 100%
        target_pct = int(scale * 100)
        # round to nearest 5
        rounded = round(target_pct / 5) * 5
        rounded = max(50, min(100, rounded))
        return zoom_font_lookup.get(rounded, font)

    def make_frame(t: float) -> np.ndarray:
        progress = t / duration
        scale = start_scale + (end_scale - start_scale) * progress

        new_w = int(w * scale)
        new_h = int(h * scale)
        zoomed = Image.fromarray(img_array).resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        frame = zoomed.crop((left, top, left + w, top + h)).convert("RGBA")
        draw = ImageDraw.Draw(frame)

        # ── TYPEWRITER ──────────────────────────────────────────────────────────
        if animation == "typewriter":
            char_offset = 0
            for i, line in enumerate(lines):
                line_start = INTRO_DUR + char_offset * TYPEWRITER_MS_PER_CHAR
                char_offset += len(line)
                if t < line_start:
                    continue
                elapsed = t - line_start
                chars_shown = min(len(line), int(elapsed / TYPEWRITER_MS_PER_CHAR))
                if chars_shown <= 0:
                    continue
                partial = line[:chars_shown]
                # Position based on full line width so cursor stays left-aligned
                full_bbox = draw.textbbox((0, 0), line, font=font)
                lx = (w - (full_bbox[2] - full_bbox[0])) / 2
                ly = start_y + i * line_h
                draw.text((lx + 2, ly + 2), partial, font=font, fill=(0, 0, 0, 180))
                draw.text((lx, ly), partial, font=font, fill=(255, 255, 255, 255))

        # ── WORD FADE ────────────────────────────────────────────────────────────
        elif animation == "word_fade":
            for idx, (word, cx, ly) in enumerate(word_positions):
                word_start = INTRO_DUR + idx * WORD_FADE_MS_PER_WORD
                if t < word_start:
                    continue
                elapsed = t - word_start
                alpha = int(255 * min(1.0, elapsed / WORD_FADE_FADE_DUR))
                if alpha <= 0:
                    continue
                draw.text((cx + 2, ly + 2), word, font=font, fill=(0, 0, 0, min(alpha, 180)))
                draw.text((cx, ly), word, font=font, fill=(255, 255, 255, alpha))

        # ── SLIDE UP ─────────────────────────────────────────────────────────────
        elif animation == "slide_up":
            for idx, (word, cx, ly) in enumerate(word_positions):
                word_start = INTRO_DUR + idx * SLIDE_UP_MS_PER_WORD
                if t < word_start:
                    continue
                elapsed = t - word_start
                progress_w = min(1.0, elapsed / SLIDE_UP_FADE_DUR)
                alpha = int(255 * progress_w)
                if alpha <= 0:
                    continue
                # Slide up: starts 30px below, rises to final position
                offset_y = int(30 * (1.0 - progress_w))
                draw.text((cx + 2, ly + offset_y + 2), word, font=font, fill=(0, 0, 0, min(alpha, 180)))
                draw.text((cx, ly + offset_y), word, font=font, fill=(255, 255, 255, alpha))

        # ── ZOOM IN ──────────────────────────────────────────────────────────────
        elif animation == "zoom_in":
            for idx, (word, cx, ly) in enumerate(word_positions):
                word_start = INTRO_DUR + idx * ZOOM_IN_MS_PER_WORD
                if t < word_start:
                    continue
                elapsed = t - word_start
                progress_w = min(1.0, elapsed / ZOOM_IN_FADE_DUR)
                alpha = int(255 * progress_w)
                if alpha <= 0:
                    continue
                # Scale word from 50% → 100%; center it at the full-size position
                zoom_font = _get_zoom_font(progress_w)
                full_bbox = draw.textbbox((0, 0), word, font=font)
                scaled_bbox = draw.textbbox((0, 0), word, font=zoom_font)
                full_w = full_bbox[2] - full_bbox[0]
                scaled_w = scaled_bbox[2] - scaled_bbox[0]
                x_adjust = (full_w - scaled_w) // 2
                draw.text((cx + x_adjust + 2, ly + 2), word, font=zoom_font, fill=(0, 0, 0, min(alpha, 180)))
                draw.text((cx + x_adjust, ly), word, font=zoom_font, fill=(255, 255, 255, alpha))

        # ── LINE FADE (default) ───────────────────────────────────────────────────
        else:
            for i, line in enumerate(lines):
                line_start = INTRO_DUR + i * LINE_FADE_MS_PER_LINE
                if t < line_start:
                    continue
                elapsed = t - line_start
                alpha = int(255 * min(1.0, elapsed / LINE_FADE_FADE_DUR))
                if alpha <= 0:
                    continue
                bbox = draw.textbbox((0, 0), line, font=font)
                lx = (w - (bbox[2] - bbox[0])) / 2
                ly = start_y + i * line_h
                draw.text((lx + 2, ly + 2), line, font=font, fill=(0, 0, 0, min(alpha, 180)))
                draw.text((lx, ly), line, font=font, fill=(255, 255, 255, alpha))

        return np.array(frame.convert("RGB"))

    clip = VideoClip(make_frame, duration=duration)
    clip = clip.set_fps(fps)

    output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_reel.mp4"
    output_path = os.path.join(REELS_DIR, output_filename)

    logger.info(f"[KEN BURNS] Creating reel | animation={animation} | duration={duration:.1f}s")
    clip.write_videofile(output_path, fps=fps, codec="libx264", verbose=False, logger=None)
    logger.info(f"[KEN BURNS] Reel saved: {output_path}")
    return output_path
