import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

async def generate_caption(quote: str, vibe: str = "melancholic", retries: int = 3) -> str:
    prompt = (
        f"You are a YouTube Shorts content strategist for a premium quote channel. "
        f"Given this quote: '{quote}' and vibe: '{vibe}', "
        f"write a short punchy YouTube Shorts caption (1-2 sentences max) "
        f"and add 5-7 relevant trending hashtags at the end including #Shorts. "
        f"No extra explanation, just the caption and hashtags."
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(retries):
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data['candidates'][0]['content']['parts'][0]['text'].strip()
                elif response.status_code == 429:
                    wait = 10 * (attempt + 1)
                    print(f"--- [CAPTION] 429 Rate limit. Waiting {wait}s before retry {attempt+1}/{retries} ---")
                    await asyncio.sleep(wait)
                else:
                    return f"Error: API returned {response.status_code}"
            except Exception as e:
                return f"Error: {str(e)}"

    return "✨ Some things are better felt than said. #QuoteOfTheDay #DeepThoughts #Vibes"

def save_caption(caption: str, reel_path: str):
    txt_path = os.path.splitext(reel_path)[0] + "_caption.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(caption)
    print(f"--- [CAPTION] Saved: {txt_path} ---")
    return txt_path