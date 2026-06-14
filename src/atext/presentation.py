from __future__ import annotations

from html import escape

import markdown
import nh3

_ALLOWED_TAGS = {
    "a",
    "blockquote",
    "br",
    "code",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "li",
    "ol",
    "p",
    "pre",
    "strong",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
    "ul",
}
_ALLOWED_ATTRIBUTES = {
    "a": {"href", "title"},
    "th": {"align"},
    "td": {"align"},
}
_ALLOWED_PROTOCOLS = {"http", "https", "mailto"}


def render_presented_markdown(body: str) -> str:
    """Render Markdown to sanitized HTML safe for unauthenticated public pages."""

    unsafe_html = markdown.markdown(
        body,
        extensions=["extra", "sane_lists"],
        output_format="html",
    )
    return nh3.clean(
        unsafe_html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        url_schemes=_ALLOWED_PROTOCOLS,
        link_rel="noopener noreferrer",
    )


def render_presented_page(*, body: str) -> str:
    content = render_presented_markdown(body)
    title = escape("Presented document")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8fafc;
      --surface: #ffffff;
      --text: #111827;
      --muted: #4b5563;
      --border: #e5e7eb;
      --accent: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }}
    .page {{
      max-width: 860px;
      margin: 0 auto;
      padding: 48px 20px;
    }}
    .surface {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 18px;
      box-shadow: 0 20px 45px rgba(15, 23, 42, 0.08);
      padding: clamp(24px, 5vw, 56px);
    }}
    .eyebrow {{
      color: var(--muted);
      font-size: 0.875rem;
      margin: 0 0 24px;
    }}
    .document-body :first-child {{ margin-top: 0; }}
    .document-body :last-child {{ margin-bottom: 0; }}
    .document-body h1, .document-body h2, .document-body h3 {{ line-height: 1.2; }}
    .document-body a {{ color: var(--accent); }}
    .document-body pre, .document-body code {{
      background: #f3f4f6;
      border-radius: 8px;
    }}
    .document-body code {{ padding: 0.1rem 0.25rem; }}
    .document-body pre {{ overflow: auto; padding: 1rem; }}
    .document-body blockquote {{
      border-left: 4px solid var(--border);
      color: var(--muted);
      margin-left: 0;
      padding-left: 1rem;
    }}
    .document-body table {{ border-collapse: collapse; width: 100%; }}
    .document-body th, .document-body td {{ border: 1px solid var(--border); padding: 0.5rem; }}
  </style>
</head>
<body>
  <main class="page">
    <article class="surface">
      <p class="eyebrow">Presented with atext</p>
      <div class="document-body">
{content}
      </div>
    </article>
  </main>
</body>
</html>"""
