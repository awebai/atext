# Preview a naapp page design faithfully without standing up the app or a DB

To iterate on a naapp page design (library/folio) against the REAL chrome and
CSS without a running server or Postgres:

1. Render through the real toolkit: build a `SiteConfig` (reuse the app's
   `surfaces._site`) and call `aweb_naapp.page(site, body)` — byte-exact head,
   header, footer, theme script.
2. Make it self-contained for the browser: replace the `<link rel="stylesheet"
   href="/css/aweb.<hash>.css">` with an inline `<style>` holding
   `aweb_naapp.aweb_css()` (the served two-layer bundle), and rewrite the
   `/fonts/BerkeleyMono-*.woff2` URLs in that CSS to base64 `data:font/woff2`
   URIs (the woff2 live in the app repo's `site/static/fonts/`). Use a function
   replacement in `re.sub` — the CSS contains backslashes that break a string
   replacement's group refs.
3. Playwright blocks `file://`; serve the output dir with
   `python3 -m http.server` and navigate to `http://127.0.0.1:<port>/...`.
4. Dark mode: `document.documentElement.setAttribute('data-theme','dark')` via
   `browser_evaluate` (the aweb.css honors `:root[data-theme="dark"]`).

This validates the DESIGN faithfully. It is NOT the same as verification: the
handoff/verification screenshots must still come from the live integrated app
against seeded data (see [[../../reviewer/patterns]] and the team rule that
"verified" means a running instance, not a static render).
