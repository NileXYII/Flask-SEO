import os
from datetime import date

from flask import Flask, Response, render_template

# On Vercel, static assets live in public/ and are served from the CDN.
# Pointing Flask at the same folder keeps `python app.py` working locally.
app = Flask(__name__, static_folder="public", static_url_path="")


def site_url():
    """SITE_URL env var wins; otherwise use Vercel's production domain; else localhost."""
    if os.environ.get("SITE_URL"):
        return os.environ["SITE_URL"].rstrip("/")
    prod = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL")
    if prod:
        return f"https://{prod}"
    return "http://localhost:5000"


# ---------------------------------------------------------------------------
# Site-wide SEO settings: edit these first.
# ---------------------------------------------------------------------------
app.config["SITE"] = {
    "name": "Acme Studio",
    "url": site_url(),  # set SITE_URL in Vercel env vars for a custom domain
    "locale": "en_US",
    "twitter": "@acmestudio",  # or "" to omit
    "default_image": "/img/og-default.png",  # 1200x630
}

SITE = app.config["SITE"]


def org_schema():
    return {
        "@type": "Organization",
        "@id": f"{SITE['url']}/#org",
        "name": SITE["name"],
        "url": SITE["url"],
        "logo": f"{SITE['url']}/img/logo.png",
    }


# ---------------------------------------------------------------------------
# Per-page SEO. One dict per page; the template reads `seo`.
# ---------------------------------------------------------------------------
def seo_home():
    return {
        "title": "Acme Studio: Fast, accessible web projects",
        "description": "Acme Studio builds fast, accessible Flask web apps with Material Design 3. "
        "Explore guides, tools and case studies.",
        "path": "/",
        "keywords": "flask, material design 3, web development, seo",
        "schema": {
            "@context": "https://schema.org",
            "@graph": [
                org_schema(),
                {
                    "@type": "WebSite",
                    "@id": f"{SITE['url']}/#website",
                    "url": SITE["url"],
                    "name": SITE["name"],
                    "publisher": {"@id": f"{SITE['url']}/#org"},
                },
            ],
        },
    }


def seo_content():
    url = f"{SITE['url']}/guide/flask-seo-meta-tags"
    return {
        "title": "The complete guide to SEO meta tags in Flask",
        "description": "Learn every SEO meta tag a Flask site needs: titles, descriptions, canonicals, "
        "robots, Open Graph, Twitter cards and JSON-LD, with copy-paste code.",
        "path": "/guide/flask-seo-meta-tags",
        "type": "article",
        "published": "2026-10-26",
        "modified": "2026-10-26",
        "author": SITE["name"],
        "keywords": "flask seo, meta tags, open graph, canonical url, json-ld, jinja2",
        "schema": {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "Article",
                    "headline": "The complete guide to SEO meta tags in Flask",
                    "datePublished": "2026-10-26",
                    "dateModified": "2026-10-26",
                    "author": {"@type": "Organization", "name": SITE["name"]},
                    "publisher": {"@id": f"{SITE['url']}/#org"},
                    "mainEntityOfPage": url,
                    "image": f"{SITE['url']}{SITE['default_image']}",
                },
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["url"] + "/"},
                        {"@type": "ListItem", "position": 2, "name": "Guide", "item": url},
                    ],
                },
            ],
        },
    }


def seo_about():
    return {
        "title": "About us",
        "description": "Meet the team behind Acme Studio and learn how we build fast, "
        "accessible and search-friendly websites.",
        "path": "/about",
        "schema": {
            "@context": "https://schema.org",
            "@type": "AboutPage",
            "name": "About Acme Studio",
            "url": f"{SITE['url']}/about",
            "about": org_schema(),
        },
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.after_request
def keep_previews_out_of_search(resp):
    """Vercel preview/dev deployments must never be indexed."""
    if os.environ.get("VERCEL_ENV") in ("preview", "development"):
        resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp


@app.route("/")
def home():
    return render_template("home.html", seo=seo_home())


@app.route("/guide/flask-seo-meta-tags")
def content():
    return render_template("content.html", seo=seo_content())


@app.route("/about")
def about():
    return render_template("about.html", seo=seo_about())


@app.route("/robots.txt")
def robots():
    body = f"User-agent: *\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    pages = [seo_home(), seo_content(), seo_about()]
    today = date.today().isoformat()
    urls = "".join(
        f"<url><loc>{SITE['url']}{p['path']}</loc>"
        f"<lastmod>{p.get('modified', today)}</lastmod></url>"
        for p in pages
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>"
    )
    return Response(xml, mimetype="application/xml")


@app.errorhandler(404)
def not_found(_):
    seo = {
        "title": "Page not found",
        "description": "The page you are looking for does not exist.",
        "path": "/404",
        "robots": "noindex, nofollow",
    }
    return render_template("about.html", seo=seo, not_found=True), 404


if __name__ == "__main__":
    app.run(debug=True)
