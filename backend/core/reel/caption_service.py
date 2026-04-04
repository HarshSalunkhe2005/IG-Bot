import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

async def generate_caption(short_caption: str, quote: str, vibe: str = "melancholic", retries: int = 3) -> str:
    """
    Generate YouTube description: '{short_caption}\n\n{hashtags}'
    short_caption is the 1-3 word caption from Gemini (e.g. "Growth", "Inner Silence").
    """
    prompt = (
        f"You are a YouTube Shorts content strategist. "
        f"Given this quote: '{quote}' and vibe: '{vibe}', "
        f"generate 5-7 relevant trending hashtags including #Shorts. "
        f"Return ONLY the hashtags separated by spaces, no explanation, no extra text."
    )

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(retries):
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    hashtags = data['candidates'][0]['content']['parts'][0]['text'].strip()
                    return f"{short_caption}\n\n{hashtags}"
                elif response.status_code == 429:
                    wait = 10 * (attempt + 1)
                    print(f"--- [CAPTION] 429 Rate limit. Waiting {wait}s before retry {attempt+1}/{retries} ---")
                    await asyncio.sleep(wait)
                else:
                    return f"{short_caption}\n\n#QuoteOfTheDay #DeepThoughts #Shorts"
            except Exception as e:
                return f"{short_caption}\n\n#QuoteOfTheDay #DeepThoughts #Shorts"

    return f"{short_caption}\n\n#QuoteOfTheDay #DeepThoughts #Vibes #Shorts"

def save_caption(caption: str, reel_path: str):
    txt_path = os.path.splitext(reel_path)[0] + "_caption.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(caption)
    print(f"--- [CAPTION] Saved: {txt_path} ---")
    return txt_path