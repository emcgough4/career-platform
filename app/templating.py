import re
from datetime import date

from urllib.parse import parse_qs, urlparse

from fastapi.templating import Jinja2Templates

from app.config import settings

templates = Jinja2Templates(directory="templates")

SENTENCE_BREAK = re.compile(r"(?:(?<=[.!?])|(?<=[.!?][”\"’]))\s+(?=[A-Z“\"])")


def month_year(value: date | str | None) -> str:
    """Render a date (or ISO date string from the snapshot) as 'Jan 2026'."""
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = date.fromisoformat(value[:10])
        except ValueError:
            return value
    return value.strftime("%b %Y")


def sentences(text: str | None) -> list[str]:
    """Split a description paragraph into sentences for bulleted display."""
    if not text:
        return []
    return [part.strip() for part in SENTENCE_BREAK.split(text.strip()) if part.strip()]


VIDEO_EXTENSIONS = (".mp4", ".webm", ".mov", ".m4v")


def is_video(url: str | None) -> bool:
    """True when a media URL points at a video file rather than an image."""
    return bool(url) and urlparse(url).path.lower().endswith(VIDEO_EXTENSIONS)


def embed_url(url: str | None) -> str:
    """Turn a YouTube, TikTok or Instagram post link into its embeddable player URL ('' otherwise)."""
    if not url:
        return ""
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.").removeprefix("m.")
    parts = [part for part in parsed.path.split("/") if part]
    if host == "youtu.be" and parts:
        return f"https://www.youtube-nocookie.com/embed/{parts[0]}"
    if host == "youtube.com":
        video_id = parse_qs(parsed.query).get("v", [""])[0]
        if not video_id and len(parts) >= 2 and parts[0] in ("shorts", "embed", "live"):
            video_id = parts[1]
        return f"https://www.youtube-nocookie.com/embed/{video_id}" if video_id else ""
    if host == "tiktok.com" and "video" in parts:
        index = parts.index("video")
        if index + 1 < len(parts):
            return f"https://www.tiktok.com/embed/v2/{parts[index + 1]}"
    if host == "instagram.com" and len(parts) >= 2 and parts[0] in ("reel", "reels", "p", "tv"):
        return f"https://www.instagram.com/{'reel' if parts[0] == 'reels' else parts[0]}/{parts[1]}/embed"
    return ""


templates.env.filters["month_year"] = month_year
templates.env.filters["is_video"] = is_video
templates.env.filters["embed_url"] = embed_url
templates.env.globals["preview_slots"] = settings.preview_slots
templates.env.filters["sentences"] = sentences
