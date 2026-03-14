import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"
HISTORY_FILE = os.path.join("outputs", "history.json")

def load_history():
    """Reads used quotes from the JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return []

async def generate_quote(vibe: str = "melancholic"):
    """Generates a unique 2-line quote and checks against history."""
    history = load_history()
    # Get just the text of previous quotes for comparison
    used_quotes = [item['quote'] for item in history]

    prompt = (
        f"Write a 2-line deep, {vibe} quote in English. Vibe: {vibe}. "
        f"Ensure it is NOT one of these: {used_quotes[-10:] if used_quotes else 'None'}. "
        "No hashtags, no extra text."
    )
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                quote = data['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Double check uniqueness locally
                if quote in used_quotes:
                    return await generate_quote(vibe) # Recursive retry
                
                return quote
            return f"Error: API returned {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"