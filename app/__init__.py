"""Flask app factory: configures FlatPages and wires helpers, routes, and hooks."""

from datetime import datetime
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for

from .extensions import pages
from .utils.dates import format_datetime
from .utils.posts import reading_time
from .utils.urls import absolute_url, get_site_url, slugify_tag


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app():
    load_dotenv(BASE_DIR / ".env")  # .env holds SITE_URL etc.

    flask_app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    # Fail closed: indexing must be explicitly enabled in the launch environment.
    flask_app.config["NOINDEX"] = (
        os.getenv("NOINDEX", "True").strip().lower() == "true"
    )

    flask_app.config["FLATPAGES_EXTENSION"] = ".md"
    flask_app.config["FLATPAGES_ROOT"] = str(BASE_DIR / "posts")
    flask_app.config["FLATPAGES_MARKDOWN_EXTENSIONS"] = [
        "fenced_code",
        "codehilite",
        "tables",
        "toc",  # generates header ids so in-page anchor links (#section-name) work
    ]

    pages.init_app(flask_app)

    register_template_helpers(flask_app)
    register_routes(flask_app)
    register_hooks(flask_app)
    register_error_handlers(flask_app)

    return flask_app


def register_template_helpers(flask_app):
    # Jinja filters, plus globals (inject_now) available in every template.
    flask_app.add_template_filter(format_datetime, "strftime")
    flask_app.add_template_filter(reading_time, "reading_time")
    # single source of truth for tag slugs — templates must not hand-build them
    flask_app.add_template_filter(slugify_tag, "slugify_tag")

    @flask_app.context_processor
    def inject_now():
        return {
            "now": datetime.now(),
            "noindex": flask_app.config["NOINDEX"],
            "site_url": get_site_url(),
            "canonical_url": absolute_url(request.path),
            "default_image_url": absolute_url(
                url_for("static", filename="images/og-image.jpg")
            ),
        }


def register_routes(flask_app):
    # Imported here (not at top) to avoid circular imports with this package.
    from .routes.feeds import bp as feeds_bp
    from .routes.pages import bp as pages_bp

    flask_app.register_blueprint(pages_bp)
    flask_app.register_blueprint(feeds_bp)


def register_hooks(flask_app):
    # Baseline security headers on every response.
    @flask_app.after_request
    def add_security_headers(response):
        # Pre-launch: tell crawlers not to index anything (see NOINDEX in .env)
        if flask_app.config["NOINDEX"]:
            response.headers.setdefault("X-Robots-Tag", "noindex, nofollow")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        # Disallow embedding the site in iframes (clickjacking protection)
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        return response


def register_error_handlers(flask_app):
    # Friendly 404 / 500 pages.
    @flask_app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @flask_app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500


app = create_app()
