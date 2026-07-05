"""Blog post helpers over Flask-FlatPages: sorting, navigation, tags, reading time."""

from datetime import date
import re

from app.extensions import pages

from .dates import normalize_post_date


def get_sorted_posts():
    """Return dated posts, newest first."""
    # Drafts without a date are excluded; undated edge cases sort to date.min.
    posts = [post for post in pages if "date" in post.meta]
    posts.sort(
        key=lambda post: normalize_post_date(post.meta.get("date")) or date.min,
        reverse=True,
    )
    return posts


def get_prev_next(current_path):
    """Return (prev, next) posts for navigation, or (None, None) if not found."""
    posts = get_sorted_posts()
    try:
        idx = next(i for i, post in enumerate(posts) if post.path == current_path)
    except StopIteration:
        return None, None

    # List is newest-first, so the newer post sits at idx-1, the older at idx+1.
    next_post = posts[idx - 1] if idx > 0 else None
    prev_post = posts[idx + 1] if idx + 1 < len(posts) else None
    return prev_post, next_post


def get_all_tags():
    """Return the sorted set of unique tags across all posts."""
    tags = set()
    for post in get_sorted_posts():
        for tag in post.meta.get("tags") or []:
            tags.add(tag)
    return sorted(tags)


def reading_time(text):
    """Estimate reading time; CJK counts per-character (~500 cpm), words at ~200 wpm."""
    if not text:
        return ""

    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    # CJK has no word boundaries — count characters and words separately.
    cjk_count = len(re.findall(r"[一-鿿]", prose))
    word_count = len(re.findall(r"\b\w+\b", re.sub(r"[一-鿿]", "", prose)))
    minutes = max(1, round(cjk_count / 500 + word_count / 200))
    return f"閱讀時間約 {minutes} 分鐘"
