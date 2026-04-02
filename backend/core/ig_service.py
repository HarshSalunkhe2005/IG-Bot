# backend/core/ig_service.py

import os
import httpx
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# IG credentials from .env
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
IG_BUSINESS_ACCOUNT_ID = os.getenv("IG_BUSINESS_ACCOUNT_ID")
print(f"[IG SERVICE] DEBUG - Account ID: {IG_BUSINESS_ACCOUNT_ID}")
print(f"[IG SERVICE] DEBUG - Token exists: {bool(IG_ACCESS_TOKEN)}")
GRAPH_API_VERSION = "v18.0"

FAILED_POSTS_FILE = os.path.join("outputs", "failed_posts.json")
os.makedirs("outputs", exist_ok=True)

# Helper: Load/Save failed posts
def load_failed_posts():
    if not os.path.exists(FAILED_POSTS_FILE):
        return []
    try:
        with open(FAILED_POSTS_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_failed_posts(posts):
    with open(FAILED_POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=4)

def add_failed_post(reel_path, caption, error):
    """Store failed post for retry"""
    failed_posts = load_failed_posts()
    failed_posts.append({
        "reel_path": reel_path,
        "caption": caption,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "retry_count": 0
    })
    save_failed_posts(failed_posts)
    logger.error(f"[IG SERVICE] Failed post stored: {reel_path}")

def remove_failed_post(reel_path):
    """Remove from failed posts after successful retry"""
    failed_posts = load_failed_posts()
    failed_posts = [p for p in failed_posts if p["reel_path"] != reel_path]
    save_failed_posts(failed_posts)

def increment_retry_count(reel_path):
    """Increment retry attempts, delete after 3 failures"""
    failed_posts = load_failed_posts()
    for post in failed_posts:
        if post["reel_path"] == reel_path:
            post["retry_count"] += 1
            if post["retry_count"] >= 3:
                logger.warning(f"[IG SERVICE] Max retries reached for {reel_path}. Deleting.")
                failed_posts = [p for p in failed_posts if p["reel_path"] != reel_path]
            break
    save_failed_posts(failed_posts)

# Helper: Error suggestions
def get_error_suggestion(error_msg):
    """Provide actionable suggestion based on error"""
    if "invalid" in error_msg.lower() and "token" in error_msg.lower():
        return "Invalid or expired Instagram token. Check IG_ACCESS_TOKEN in .env"
    elif "rate" in error_msg.lower():
        return "Rate limit hit. Wait a moment and retry."
    elif "media" in error_msg.lower():
        return "Issue with media. Ensure video is MP4, <100MB, and caption is valid."
    elif "network" in error_msg.lower():
        return "Network error. Check connection and retry."
    else:
        return "Unknown error. Check logs for details."

async def post_reel_to_instagram(reel_path: str, caption: str) -> dict:
    """
    Upload reel to Instagram via Graph API.
    Returns: { success: bool, post_url: str or error: str, suggestion: str }
    """
    try:
        # Construct video URL
        clean_path = reel_path.replace("outputs/", "").replace("\\", "/")
        video_url = f"http://localhost:8000/outputs/{clean_path}"
        logger.info(f"[IG SERVICE] Posting to IG - Video: {video_url}")
        logger.info(f"[IG SERVICE] Caption: {caption[:50]}...")

        async with httpx.AsyncClient(timeout=120.0) as client:
            # Step 1: Create media container
            media_url = f"https://graph.instagram.com/{GRAPH_API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media"
            media_payload = {
                "media_type": "VIDEO",
                "video_url": video_url,
                "caption": caption,
                "access_token": IG_ACCESS_TOKEN
            }

            logger.info("[IG SERVICE] Creating media container...")
            media_resp = await client.post(media_url, json=media_payload)

            if media_resp.status_code != 200:
                error_text = media_resp.text
                logger.error(f"[IG SERVICE] Media creation failed: {error_text}")
                return {
                    "success": False,
                    "error": f"Failed to create media container: {media_resp.status_code}",
                    "suggestion": get_error_suggestion(error_text)
                }

            media_data = media_resp.json()
            creation_id = media_data.get("id")
            logger.info(f"[IG SERVICE] Media container created: {creation_id}")

            # Step 2: Publish media
            publish_url = f"https://graph.instagram.com/{GRAPH_API_VERSION}/{IG_BUSINESS_ACCOUNT_ID}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": IG_ACCESS_TOKEN
            }

            logger.info("[IG SERVICE] Publishing media...")
            publish_resp = await client.post(publish_url, json=publish_payload)

            if publish_resp.status_code != 200:
                error_text = publish_resp.text
                logger.error(f"[IG SERVICE] Publishing failed: {error_text}")
                return {
                    "success": False,
                    "error": f"Failed to publish: {publish_resp.status_code}",
                    "suggestion": get_error_suggestion(error_text)
                }

            publish_data = publish_resp.json()
            post_id = publish_data.get("id")
            post_url = f"https://www.instagram.com/p/{post_id}/"

            logger.info(f"[IG SERVICE] Success! Post URL: {post_url}")

            return {
                "success": True,
                "post_url": post_url,
                "post_id": post_id,
                "message": "Reel posted successfully to Instagram!"
            }

    except httpx.TimeoutException:
        error = "Request timeout. Network might be slow."
        logger.error(f"[IG SERVICE] Timeout: {error}")
        add_failed_post(reel_path, caption, error)
        return {
            "success": False,
            "error": error,
            "suggestion": "Check your network connection and retry."
        }
    except Exception as e:
        error = str(e)
        logger.error(f"[IG SERVICE] Unexpected error: {error}")
        add_failed_post(reel_path, caption, error)
        return {
            "success": False,
            "error": error,
            "suggestion": "An unexpected error occurred. Check logs and retry."
        }
