# Formosa Digital

Flask site for **formosadigital.com** — same architecture and design as `main-site` (jakewang.dev), without the dashboards.

## Structure

```
app.py                  # Entry point (port 5001)
app/
  __init__.py           # App factory: FlatPages config, filters, security headers
  extensions.py         # Shared FlatPages instance (avoids circular imports)
  routes/
    pages.py            # /, /blog/, /blog/<path>/, /blog/tag/<slug>/
    feeds.py            # /robots.txt, /sitemap.xml
  utils/
    urls.py             # SITE_URL helpers + tag slugs
    dates.py            # Front-matter date coercion / formatting
    posts.py            # Post sorting, prev/next, tags, reading time (CJK-aware)
    schema.py           # JSON-LD builders (Organization-based, zh-Hant)
posts/                  # Markdown posts (front-matter: title/date/description/category/tags)
templates/              # zh-Hant-TW templates, shared base.html
static/css/style.css    # Copied from main-site — keep visual parity manually
```

## Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
FLASK_DEBUG=True python app.py   # http://localhost:5001
```

## Differences from main-site

- Organization JSON-LD (not Person), `inLanguage: zh-Hant`, `og:locale zh_TW`
- No dashboards, no dashboard.js, no API_URL
- `reading_time` counts CJK characters (~500 cpm)

## TODO before launch

- [ ] Replace `static/images/og-image.jpg` and favicon (currently main-site placeholders)
- [ ] Add GTM / analytics snippet in `base.html`
- [ ] Add google-site-verification meta after registering Search Console
- [ ] Refine homepage intro and meta descriptions (marked `TODO` in code)
- [ ] Deploy: systemd unit (gunicorn, port 5001) + nginx server block + certbot on web-01
