import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"
HISTORY_FILE = os.path.join("outputs", "history.json")

VIBE_FONT_HINTS = {
    "melancholic": "elegant serif fonts like Cormorant Garamond, Bodoni Moda, or Playfair Display",
    "modern": "clean sans-serif fonts like DM Sans, Space Grotesk, or Josefin Sans",
    "personal": "beautiful cursive or handwritten fonts like Dancing Script, Great Vibes, or Pacifico",
    "bold": "strong heavy fonts like Bebas Neue, Righteous, or Black Han Sans",
    "minimalist": "ultra-light sans-serif fonts like Raleway, Nunito, or Quicksand"
}

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

async def generate_quote(vibe: str = "melancholic"):
    history = load_history()
    used_quotes = [item['quote'] for item in history]
    font_hint = VIBE_FONT_HINTS.get(vibe, "an elegant serif font")

    prompt = (
        f"You are a creative director for a premium YouTube Shorts channel. "
        f"Generate a deep, {vibe} quote in English. "
        f"Also suggest ONE perfect Google Font name that matches the vibe. "
        f"For this vibe, prefer {font_hint}. "
        f"Also provide ONE short caption (1-3 words max) that captures the essence of the quote "
        f"(e.g., 'Transformation', 'Growth', 'Becoming', 'Inner Silence'). "
        f"Ensure the quote is NOT one of these: {used_quotes[-10:] if used_quotes else 'None'}. "
        "Respond ONLY in this exact JSON format, no extra text, no markdown: "
        '{"quote": "your quote here", "font": "Google Font Name", "caption": "OneWord"}'
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                raw = data['candidates'][0]['content']['parts'][0]['text'].strip()
                raw = raw.replace("```json", "").replace("```", "").strip()

                parsed = json.loads(raw)
                quote = parsed.get("quote", "").strip()
                font = parsed.get("font", "Playfair Display").strip()
                caption = parsed.get("caption", "Reflections").strip()

                if quote in used_quotes:
                    return await generate_quote(vibe)

                return quote, font, caption

            return f"Error: API returned {response.status_code}", None, None
        except Exception as e:
            return f"Error: {str(e)}", None, None