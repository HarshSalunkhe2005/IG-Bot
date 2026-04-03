# YT-Bot

A full-stack app for generating and publishing AI-powered YouTube Shorts quote videos.

Pick a vibe → get AI-generated quotes → choose a font and animation → render a short video → post directly to YouTube.

## Stack

- **Backend**: Python / FastAPI
- **Frontend**: React (Vite)
- **AI**: Google Gemini (quotes + captions), Unsplash (background images)
- **Video**: MoviePy + Pillow (Ken Burns effect, 5 text animations)
- **Publishing**: YouTube Data API v3 (OAuth 2.0)

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Google Cloud project with **YouTube Data API v3** enabled and an OAuth 2.0 client (Desktop app type)
- A [Gemini API key](https://aistudio.google.com/app/apikey)
- An [Unsplash developer account](https://unsplash.com/developers) for background images

### 1. Clone & install dependencies

```bash
# Python
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env`:

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `UNSPLASH_ACCESS_KEY` | Unsplash API access key |
| `YOUTUBE_CLIENT_ID` | OAuth 2.0 client ID from Google Cloud Console |
| `YOUTUBE_CLIENT_SECRET` | OAuth 2.0 client secret |
| `YOUTUBE_REFRESH_TOKEN` | Refresh token obtained after completing OAuth consent flow once |

To get a YouTube refresh token, run the OAuth consent flow once with `google-auth-oauthlib` and note the token it returns.

### 3. Run

```bash
# Backend (from repo root)
python -m backend.main

# Frontend (in a separate terminal)
cd frontend && npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## How it works

1. **Vibe** — choose a mood (melancholic, modern, personal, bold, minimalist)
2. **Quote** — pick from 3 AI-generated quotes or write your own
3. **Font** — preview and select from 15 Google Fonts
4. **Animation** — choose one of 5 text animation styles (line fade, word fade, typewriter, slide up, zoom in)
5. **Post preview** — renders a 1080×1080 static image with an Unsplash background
6. **Short preview** — builds an animated vertical video (MP4) with Ken Burns zoom effect
7. **Publish** — posts the short directly to YouTube via the Data API

Generated files are saved to `outputs/` (gitignored).
