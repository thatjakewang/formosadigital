"""URL helpers: site base URL, absolute-URL building, and tag slugs."""

import os


def get_site_url():
    # Base URL from env (SITE_URL), trailing slash stripped for clean joins.
    return os.getenv("SITE_URL", "https://formosadigital.com").rstrip("/")


def absolute_url(path):
    # Prefix a root-relative path with the site URL; pass through full URLs.
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return get_site_url() + path


def slugify_tag(tag):
    # Single source of truth for tag slugs (must match the tag routes).
    return tag.lower().replace(" ", "-")
