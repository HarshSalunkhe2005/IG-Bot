import os
import io
import re
import httpx
from PIL import ImageFont

DEFAULT_FONT = "Playfair Display"


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
