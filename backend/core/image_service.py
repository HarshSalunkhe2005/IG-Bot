import os
import uuid
from google import genai
from google.genai import types

# Path setup
TEMP_BG_DIR = os.path.join("outputs", "temp_bg")

# Initialize Client (Ensure GEMINI_API_KEY is in your .env)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_background_image(quote_text, vibe="melancholic"):
    """Generates a native Gemini image based on the quote's soul."""
    try:
        # Prompt logic to get that 'Pro' texture look
        prompt = (
            f"A minimalist, professional 1080x1080 background texture. "
            f"Vibe: {vibe}. Emotional context: {quote_text}. "
            "Style: Abstract, premium dark marble or silk texture, high-end photography, "
            "no text, no people, centered negative space for typography."
        )

        # Generate using the native Flash Image model
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            )
        )

        # Extract the image from the multimodal response
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                temp_filename = f"ai_bg_{uuid.uuid4().hex[:8]}.jpg"
                temp_path = os.path.join(TEMP_BG_DIR, temp_filename)
                
                # Using the SDK's built-in helper to save the Image object
                img = part.as_image()
                img.save(temp_path)
                return temp_path

        return None
    except Exception as e:
        print(f"GenAI Image Error: {e}")
        return None