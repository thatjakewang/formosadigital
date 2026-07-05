"""Crawler-facing SEO endpoints: robots.txt and a dynamic sitemap.xml."""

from xml.sax.saxutils import escape

from flask import Blueprint, Response, current_app, url_for

from app.utils.dates import normalize_post_date
from app.utils.posts import get_all_tags, get_sorted_posts
from app.utils.urls import get_site_url, slugify_tag


bp = Blueprint("feeds", __name__)


@bp.route("/robots.txt")
def robots():
    # A route (not a static file) so it resolves at the domain root.
    return current_app.send_static_file("robots.txt")


@bp.route("/sitemap.xml")
def sitemap():
    """Build sitemap.xml from current pages, tags, and posts.

    priority is a relative crawl hint (0.0-1.0); URLs must be absolute.
    """
    base_url = get_site_url()

    # Fixed top-level pages.
    sitemap_urls = [
        {"loc": base_url + "/", "priority": "1.0"},
        {"loc": base_url + "/blog/", "priority": "0.9"},
    ]

    # One entry per tag; slugify_tag keeps URLs matching the real routes.
    for tag in get_all_tags():
        sitemap_urls.append(
            {
                "loc": base_url + url_for("pages.tag_page", tag_slug=slugify_tag(tag)),
                "priority": "0.6",
            }
        )

    # One entry per post; lastmod (post date) hints at re-crawl freshness.
    for post in get_sorted_posts():
        post_date = normalize_post_date(post.meta.get("date"))
        lastmod = post_date.isoformat() if post_date else ""

        sitemap_urls.append(
            {
                "loc": base_url + url_for("pages.post", path=post.path),
                "lastmod": lastmod,
                "priority": "0.7",
            }
        )

    # Serialize to the sitemap schema; escape() guards against stray &, <, >.
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in sitemap_urls:
        xml += "  <url>\n"
        xml += f'    <loc>{escape(page["loc"])}</loc>\n'
        if page.get("lastmod"):
            xml += f'    <lastmod>{page["lastmod"]}</lastmod>\n'
        xml += f'    <priority>{page["priority"]}</priority>\n'
        xml += "  </url>\n"

    xml += "</urlset>"

    return Response(xml, mimetype="application/xml")
