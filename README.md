# Flask SEO Meta Tags (MD3)

Copy-paste SEO for Flask. One partial, one `seo` dict per page.

## Run
```bash
pip install flask
python app.py
```
Pages: `/`, `/guide/flask-seo-meta-tags`, `/about`, plus `/sitemap.xml` and `/robots.txt`.

## Deploy to Vercel
```bash
npm i -g vercel
vercel          # preview
vercel --prod   # production
```
- Vercel detects `app.py` and the `app` Flask instance automatically; dependencies come from `requirements.txt`.
- Static files live in `public/` (served from the CDN), not Flask's static folder. Flask is pointed at `public/` too, so `python app.py` behaves the same locally.
- Canonical URLs, `og:url` and the sitemap use `SITE_URL` if set (add it under Project Settings > Environment Variables for a custom domain, e.g. `https://example.com`), otherwise Vercel's production domain.
- Local emulation: `vercel dev` (CLI 48.2.10 or newer).

## Use in your own project
1. Copy `templates/_seo.html` into your templates folder.
2. Copy the `SITE` config and `site_url()` from `app.py`, and set the `SITE_URL` env var.
3. Put your static files in `public/`. In your base template: `{% include "_seo.html" %}` inside `<head>`.
4. In each route: `render_template("page.html", seo={...})`.

### `seo` keys
| Key | Required | Notes |
|---|---|---|
| title | yes | 50-60 chars. Site name is appended automatically (except on `/`). |
| description | yes | 120-155 chars, unique per page. |
| path | yes | Canonical path, e.g. `/about`. |
| image | no | Absolute URL or `/static/...`, 1200x630. |
| type | no | `website` (default) or `article`. |
| robots | no | Default `index, follow, max-image-preview:large`. Use `noindex, nofollow` for private pages. |
| published / modified / author | no | Used for `article`. |
| schema | no | Dict rendered as JSON-LD. |

## Before launch
- Add `public/img/og-default.png` (1200x630), `favicon.svg`, `apple-touch-icon.png`, `logo.png`.
- Validate with Google Rich Results Test and the Facebook Sharing Debugger.
- Submit `/sitemap.xml` in Search Console.
