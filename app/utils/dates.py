"""Post-date helpers: coerce front-matter dates and format them for display."""

from datetime import date, datetime


def normalize_post_date(raw):
    # Front-matter dates arrive as datetime, date, or ISO string — coerce to a
    # plain date, or None if unparseable.
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str):
        try:
            return date.fromisoformat(raw)
        except ValueError:
            return None
    return None


def format_datetime(value, format="%Y-%m-%d"):
    # Jinja "strftime" filter; returns "" for missing/unparseable dates.
    if value is None:
        return ""

    normalized = normalize_post_date(value)
    if normalized:
        return normalized.strftime(format)

    return ""
