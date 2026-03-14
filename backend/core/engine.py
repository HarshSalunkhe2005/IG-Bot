import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# Using the stable v1 endpoint and Gemini 2.5 Flash as verified earlier
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

async def generate_quote(vibe: str = "melancholic"):
    """
    Generates a 2-line English quote/shayari based on a specific vibe.
    """
    prompt = f"Write a 2-line deep, {vibe} quote in English. Vibe: {vibe}. No hashtags, no extra text."
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                # Extracting the text from the Gemini response structure
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
            else:
                return f"Error: API returned {response.status_code}"
                
        except Exception as e:
            return f"Error: {str(e)}"