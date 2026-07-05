"""Page routes: home, blog index, posts, and tag pages.

Each view also assembles its schema.org JSON-LD for SEO.
"""

from flask import Blueprint, abort, render_template, url_for

from app.extensions import pages
from app.utils.dates import format_datetime
from app.utils.posts import get_all_tags, get_prev_next, get_sorted_posts
from app.utils.schema import (
    SITE_NAME,
    breadcrumb_schema,
    org_ref,
    org_schema,
    schema_graph,
    website_ref,
)
from app.utils.urls import absolute_url, get_site_url, slugify_tag


bp = Blueprint("pages", __name__)


@bp.route("/")
def home():
    # Landing page: 5 most-recent posts + WebPage JSON-LD.
    recent_posts = get_sorted_posts()[:5]
    meta_description = "Formosa Digital — 數位觀察與實作筆記。"  # TODO: refine copy
    structured_data = schema_graph(
        {
            "@type": "WebPage",
            "@id": get_site_url() + "/#webpage",
            "url": get_site_url() + "/",
            "name": SITE_NAME,
            "description": meta_description,
            "inLanguage": "zh-Hant",
            "isPartOf": website_ref(),
        }
    )
    return render_template(
        "index.html",
        posts=recent_posts,
        meta_title=SITE_NAME,
        meta_description=meta_description,
        structured_data=structured_data,
    )


@bp.route("/blog/")
def blog():
    # Blog index: all posts, tag list, and a Blog + BlogPosting JSON-LD listing.
    posts = get_sorted_posts()
    blog_url = absolute_url(url_for(".blog"))
    meta_description = "Formosa Digital 部落格 — 文章列表。"  # TODO: refine copy
    structured_data = schema_graph(
        {
            "@type": "Blog",
            "@id": blog_url + "#blog",
            "url": blog_url,
            "name": f"{SITE_NAME} Blog",
            "description": meta_description,
            "inLanguage": "zh-Hant",
            "publisher": org_ref(),
            "isPartOf": website_ref(),
            "blogPost": [
                {
                    "@type": "BlogPosting",
                    "headline": post.meta.get("title"),
                    "url": absolute_url(url_for(".post", path=post.path)),
                    "datePublished": format_datetime(post.meta.get("date")),
                }
                for post in posts
            ],
        }
    )
    return render_template(
        "blog.html",
        posts=posts,
        tags=get_all_tags(),
        meta_title=f"部落格 - {SITE_NAME}",
        meta_description=meta_description,
        structured_data=structured_data,
    )


@bp.route("/blog/<path:path>/")
def post(path):
    # Single post; 404 if the flat-page path is unknown. Builds Article + breadcrumb.
    page = pages.get_or_404(path)
    post_url = absolute_url(url_for(".post", path=page.path))
    title = page.meta.get("title", "Blog Post")
    description = page.meta.get("description", f"{title} - {SITE_NAME}")
    post_date = format_datetime(page.meta.get("date"))
    prev_post, next_post = get_prev_next(page.path)

    article_data = {
        "@type": "BlogPosting",
        "@id": post_url + "#article",
        "mainEntityOfPage": post_url,
        "headline": title,
        "description": description,
        "url": post_url,
        "datePublished": post_date,
        "dateModified": post_date,
        "inLanguage": "zh-Hant",
        "author": org_schema(),
        "publisher": org_schema(),
        "isPartOf": {"@id": absolute_url(url_for(".blog")) + "#blog"},
    }
    if page.meta.get("category"):
        article_data["articleSection"] = page.meta.get("category")

    breadcrumb_data = breadcrumb_schema(
        ("首頁", get_site_url() + "/"),
        ("部落格", absolute_url(url_for(".blog"))),
        (title, post_url),
    )

    # Articles carry their own author/publisher nodes, so no site-wide graph here
    structured_data = {
        "@context": "https://schema.org",
        "@graph": [article_data, breadcrumb_data],
    }

    return render_template(
        "post.html",
        page=page,
        prev_post=prev_post,
        next_post=next_post,
        meta_title=f"{title} - {SITE_NAME}",
        meta_description=description,
        structured_data=structured_data,
    )


@bp.route("/blog/tag/<string:tag_slug>/")
def tag_page(tag_slug):
    # Posts for one tag; 404 on unknown slug. CollectionPage JSON-LD.
    known_slugs = {slugify_tag(tag): tag for tag in get_all_tags()}
    if tag_slug not in known_slugs:
        abort(404)

    display = known_slugs[tag_slug]
    tagged_posts = [
        post
        for post in get_sorted_posts()
        if any(slugify_tag(tag) == tag_slug for tag in (post.meta.get("tags") or []))
    ]
    tag_url = absolute_url(url_for(".tag_page", tag_slug=tag_slug))
    meta_description = f"{SITE_NAME} 部落格中標記為「{display}」的所有文章。"
    structured_data = schema_graph(
        {
            "@type": "CollectionPage",
            "@id": tag_url + "#page",
            "url": tag_url,
            "name": f"{display} — {SITE_NAME}",
            "description": meta_description,
            "inLanguage": "zh-Hant",
            "isPartOf": website_ref(),
        },
        breadcrumb_schema(
            ("首頁", get_site_url() + "/"),
            ("部落格", absolute_url(url_for(".blog"))),
            (display, tag_url),
        ),
    )
    return render_template(
        "tag.html",
        tag=display,
        tag_slug=tag_slug,
        posts=tagged_posts,
        meta_title=f"{display} - {SITE_NAME}",
        meta_description=meta_description,
        structured_data=structured_data,
    )
