import re
from datetime import date

from fastapi.templating import Jinja2Templates

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


templates.env.filters["month_year"] = month_year
templates.env.filters["sentences"] = sentences
