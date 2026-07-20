"""JSON-LD (schema.org) builders for SEO structured data."""

from .urls import get_site_url

SITE_NAME = "Formosa Digital"


def org_schema():
    # Site-wide Organization node; the stable @id lets other nodes reference it.
    return {
        "@type": "Organization",
        "@id": get_site_url() + "/#organization",
        "name": SITE_NAME,
        "url": get_site_url() + "/",
    }


def org_ref():
    # Lightweight reference to the site-wide Organization node by @id.
    return {"@id": get_site_url() + "/#organization"}


def website_ref():
    # Lightweight reference to the site-wide WebSite node by @id.
    return {"@id": get_site_url() + "/#website"}


def website_schema():
    # Site-wide WebSite node, linked to the Organization via @id.
    return {
        "@type": "WebSite",
        "@id": get_site_url() + "/#website",
        "name": SITE_NAME,
        "url": get_site_url() + "/",
        "inLanguage": "zh-Hant",
        "publisher": org_ref(),
    }


def breadcrumb_schema(*crumbs):
    """BreadcrumbList node from ordered (name, url) pairs. SEO only — not rendered as UI."""
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": position, "name": name, "item": url}
            for position, (name, url) in enumerate(crumbs, start=1)
        ],
    }


def schema_graph(*items):
    """Standard JSON-LD envelope: site-wide Organization + WebSite plus page-specific nodes."""
    return {
        "@context": "https://schema.org",
        "@graph": [org_schema(), website_schema(), *items],
    }
