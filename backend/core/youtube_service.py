# backend/core/youtube_service.py

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YouTube OAuth credentials from .env
YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN")
logger.debug(f"[YT SERVICE] DEBUG - Client ID exists: {bool(YOUTUBE_CLIENT_ID)}")
logger.debug(f"[YT SERVICE] DEBUG - Refresh token exists: {bool(YOUTUBE_REFRESH_TOKEN)}")

YOUTUBE_CATEGORY_PEOPLE_AND_BLOGS = "22"
UPLOAD_CHUNK_SIZE = 1024 * 1024  # 1 MB

FAILED_POSTS_FILE = os.path.join("outputs", "failed_posts.json")
os.makedirs("outputs", exist_ok=True)


# Helper: Load/Save failed posts
def load_failed_posts():
    if not os.path.exists(FAILED_POSTS_FILE):
        return []
    try:
        with open(FAILED_POSTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_failed_posts(posts):
    with open(FAILED_POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=4)


def add_failed_post(short_path, caption, error):
    """Store failed post for retry"""
    failed_posts = load_failed_posts()
    failed_posts.append({
        "reel_path": short_path,
        "caption": caption,
        "error": error,
        "timestamp": datetime.now().isoformat(),
        "retry_count": 0
    })
    save_failed_posts(failed_posts)
    logger.error(f"[YT SERVICE] Failed post stored: {short_path}")


def remove_failed_post(short_path):
    """Remove from failed posts after successful retry"""
    failed_posts = load_failed_posts()
    failed_posts = [p for p in failed_posts if p["reel_path"] != short_path]
    save_failed_posts(failed_posts)


def increment_retry_count(short_path):
    """Increment retry attempts, delete after 3 failures"""
    failed_posts = load_failed_posts()
    for post in failed_posts:
        if post["reel_path"] == short_path:
            post["retry_count"] += 1
            if post["retry_count"] >= 3:
                logger.warning(f"[YT SERVICE] Max retries reached for {short_path}. Deleting.")
                failed_posts = [p for p in failed_posts if p["reel_path"] != short_path]
            break
    save_failed_posts(failed_posts)


# Helper: Error suggestions
def get_error_suggestion(error_msg):
    """Provide actionable suggestion based on error"""
    error_lower = error_msg.lower()
    if "invalid" in error_lower and ("token" in error_lower or "credentials" in error_lower):
        return "Invalid or expired YouTube credentials. Check YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN in .env"
    elif "quota" in error_lower:
        return "YouTube API quota exceeded. Wait until quota resets (midnight Pacific Time)."
    elif "forbidden" in error_lower or "403" in error_lower:
        return "Permission denied. Ensure your YouTube account has upload permissions enabled."
    elif "not found" in error_lower or "404" in error_lower:
        return "Resource not found. Check your YouTube credentials in .env"
    elif "network" in error_lower or "timeout" in error_lower:
        return "Network error. Check your connection and retry."
    else:
        return "Unknown error. Check logs for details."


def _get_youtube_client():
    """Build an authenticated YouTube Data API v3 client using a refresh token."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token",
    )
    creds.refresh(Request())
    return build("youtube", "v3", credentials=creds)


async def post_short_to_youtube(short_path: str, caption: str) -> dict:
    """
    Upload a Short to YouTube via Data API v3.
    The video must be vertical (9:16), ≤ 60 seconds.
    Returns: { success: bool, post_url: str } or { success: bool, error: str, suggestion: str }
    """
    try:
        logger.info(f"[YT SERVICE] Posting to YouTube - Video: {short_path}")
        logger.info(f"[YT SERVICE] Caption: {caption[:50]}...")

        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError

        youtube = _get_youtube_client()

        # Use the first line of the caption as the title (≤100 chars)
        lines = caption.strip().split("\n")
        title = lines[0].strip()[:100] if lines else "YouTube Short"
        description = caption

        # Ensure #Shorts tag is present so YouTube recognises it as a Short
        if "#Shorts" not in title and "#shorts" not in title:
            suffix = " #Shorts"
            title = title[: 100 - len(suffix)] + suffix

        if "#Shorts" not in description and "#shorts" not in description:
            description = description + "\n\n#Shorts"

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "categoryId": YOUTUBE_CATEGORY_PEOPLE_AND_BLOGS,
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            short_path,
            mimetype="video/mp4",
            resumable=True,
            chunksize=UPLOAD_CHUNK_SIZE,
        )

        logger.info("[YT SERVICE] Starting resumable upload...")
        upload_request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = upload_request.next_chunk()
            if status:
                logger.info(f"[YT SERVICE] Upload progress: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        post_url = f"https://www.youtube.com/shorts/{video_id}"
        logger.info(f"[YT SERVICE] Success! Short URL: {post_url}")

        return {
            "success": True,
            "post_url": post_url,
            "post_id": video_id,
            "message": "Short posted successfully to YouTube!",
        }

    except Exception as e:
        # Import HttpError here to avoid top-level import failure when deps aren't installed
        try:
            from googleapiclient.errors import HttpError
            if isinstance(e, HttpError):
                error = f"YouTube API error {e.resp.status}: {e.content.decode()}"
            else:
                error = str(e)
        except ImportError:
            error = str(e)

        logger.error(f"[YT SERVICE] Error: {error}")
        add_failed_post(short_path, caption, error)
        return {
            "success": False,
            "error": error,
            "suggestion": get_error_suggestion(error),
        }
