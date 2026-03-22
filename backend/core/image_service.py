import os
import httpx
import uuid

# Path setup
TEMP_BG_DIR = os.path.join("outputs", "temp_bg")
os.makedirs(TEMP_BG_DIR, exist_ok=True)

# Vibe to Unsplash keyword mapping
VIBE_KEYWORD_MAP = {
    "melancholic": "dark moody abstract texture",
    "modern": "minimal clean architecture",
    "personal": "warm bokeh light texture",
    "bold": "dramatic dark storm texture",
    "minimalist": "soft neutral minimal texture"
}

async def generate_background_image(quote_text: str, vibe: str = "melancholic"):
    """
    Moodle Way: Hits Unsplash API with a vibe-matched keyword,
    downloads image bytes directly, saves to temp_bg.
    """
    api_key = os.getenv("UNSPLASH_ACCESS_KEY")
    keyword = VIBE_KEYWORD_MAP.get(vibe, "dark abstract texture")

    search_url = "https://api.unsplash.com/photos/random"
    headers = {"Authorization": f"Client-ID {api_key}"}
    params = {
        "query": keyword,
        "orientation": "squarish",
        "content_filter": "high"
    }

    try:
        print(f"--- [IMAGE SERVICE] Fetching Unsplash image for vibe: {vibe} ---")

        async with httpx.AsyncClient() as client:
            # Step 1: Get image metadata from Unsplash
            search_resp = await client.get(search_url, headers=headers, params=params, timeout=30.0)

            if search_resp.status_code != 200:
                print(f"--- [IMAGE SERVICE] Unsplash Error {search_resp.status_code}: {search_resp.text} ---")
                return None

            data = search_resp.json()
            image_url = data["urls"]["full"]

            # Step 2: Download the actual image bytes
            img_resp = await client.get(image_url, timeout=60.0)

            if img_resp.status_code != 200:
                print(f"--- [IMAGE SERVICE] Image Download Error {img_resp.status_code} ---")
                return None

            # Step 3: Save to temp_bg
            temp_filename = f"ai_bg_{uuid.uuid4().hex[:8]}.jpg"
            temp_path = os.path.join(TEMP_BG_DIR, temp_filename)

            with open(temp_path, "wb") as f:
                f.write(img_resp.content)

            print(f"--- [IMAGE SERVICE] Image saved: {temp_path} ---")
            return temp_path

    except Exception as e:
        print(f"--- [IMAGE SERVICE] Error: {e} ---")
        return None