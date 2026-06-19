from __future__ import annotations

import re
from html import escape
from typing import Any

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
_COLOR_VARIABLES = {
    "background": "--bg",
    "surface": "--surface",
    "text": "--text",
    "muted": "--muted",
    "border": "--border",
    "accent": "--accent",
}
_FONT_VARIABLES = {
    "body": "--font-body",
    "heading": "--font-heading",
}
_FONT_ALLOWLIST = {
    "system": 'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    "serif": 'Georgia, Cambria, "Times New Roman", Times, serif',
    "mono": 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace',
}
_NAMED_COLORS = {
    "black",
    "white",
    "transparent",
    "red",
    "green",
    "blue",
    "navy",
    "orange",
    "purple",
    "pink",
    "yellow",
    "gray",
    "grey",
}
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_RGB_COLOR_RE = re.compile(r"^rgba?\(([^)]+)\)$", re.IGNORECASE)


def _valid_rgb_color(value: str) -> bool:
    match = _RGB_COLOR_RE.fullmatch(value.strip())
    if not match:
        return False
    parts = [part.strip() for part in match.group(1).split(",")]
    if len(parts) not in {3, 4}:
        return False
    try:
        channels = [int(part) for part in parts[:3]]
    except ValueError:
        return False
    if any(channel < 0 or channel > 255 for channel in channels):
        return False
    if len(parts) == 4:
        try:
            alpha = float(parts[3])
        except ValueError:
            return False
        if alpha < 0 or alpha > 1:
            return False
    return True


def _valid_color(value: str) -> bool:
    candidate = value.strip()
    return bool(
        _HEX_COLOR_RE.fullmatch(candidate)
        or _valid_rgb_color(candidate)
        or candidate.lower() in _NAMED_COLORS
    )


def sanitize_theme_tokens(tokens: Any) -> dict[str, dict[str, str]]:
    if not isinstance(tokens, dict):
        return {}

    sanitized: dict[str, dict[str, str]] = {}
    colors = tokens.get("colors")
    if isinstance(colors, dict):
        safe_colors = {
            str(key): value.strip()
            for key, value in colors.items()
            if key in _COLOR_VARIABLES and isinstance(value, str) and _valid_color(value)
        }
        if safe_colors:
            sanitized["colors"] = safe_colors

    fonts = tokens.get("fonts")
    if isinstance(fonts, dict):
        safe_fonts = {
            str(key): value.lower().strip()
            for key, value in fonts.items()
            if key in _FONT_VARIABLES and isinstance(value, str) and value.lower().strip() in _FONT_ALLOWLIST
        }
        if safe_fonts:
            sanitized["fonts"] = safe_fonts

    return sanitized


def _theme_css(tokens: dict[str, dict[str, str]] | None) -> str:
    if not tokens:
        return ""
    declarations: list[str] = []
    for key, value in tokens.get("colors", {}).items():
        variable = _COLOR_VARIABLES.get(key)
        if variable and _valid_color(value):
            declarations.append(f"      {variable}: {value.strip()};")
    for key, value in tokens.get("fonts", {}).items():
        variable = _FONT_VARIABLES.get(key)
        family = _FONT_ALLOWLIST.get(value.lower().strip())
        if variable and family:
            declarations.append(f"      {variable}: {family};")
    if not declarations:
        return ""
    return "\n" + "\n".join(declarations) + "\n"


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


def render_presented_page(*, body: str, theme: dict[str, Any] | None = None) -> str:
    content = render_presented_markdown(body)
    safe_tokens = sanitize_theme_tokens((theme or {}).get("tokens"))
    theme_css = _theme_css(safe_tokens)
    logo_url = str((theme or {}).get("logo_url") or "")
    header = str((theme or {}).get("header") or "")
    footer = str((theme or {}).get("footer") or "")
    logo_html = (
        f'      <img class="brand-logo" src="{escape(logo_url, quote=True)}" alt="Team logo">\n'
        if logo_url
        else ""
    )
    header_html = f'      <header class="theme-header">{escape(header)}</header>\n' if header else ""
    footer_html = f'      <footer class="theme-footer">{escape(footer)}</footer>\n' if footer else ""
    title = escape("Presented document")
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#faf7f2">
  <title>{title}</title>
  <style>
    /* aweb Paper/Clay design system — token values + the prose/surface rules a
       presented document uses, reproduced from awebai/ac site/static/css/aweb.css
       (sha256 6b2acef0d614c33508fe0f4e7270b4a2770ef18fb45d856c0d3e7862f85f2c19).
       Presented docs stay in the light, branded palette; team theme tokens below
       override these defaults. */
    :root {{
      color-scheme: light;
      --bg: #faf7f2;
      --surface: #fffdf9;
      --surface-2: #f1ece4;
      --text: #1c1814;
      --muted: #5f574e;
      --faint: #8f867b;
      --border: rgba(28,24,20,0.10);
      --border-strong: rgba(28,24,20,0.17);
      --accent: #b8482b;
      --radius: 14px;
      --radius-sm: 9px;
      --shadow-lg: 0 1px 2px rgba(28,24,20,0.05), 0 14px 36px -20px rgba(28,24,20,0.30);
      --font-body: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      --font-mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
      --font-heading: var(--font-body);{theme_css}    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-body);
      font-size: clamp(0.95rem, 0.92rem + 0.15vw, 1rem);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
    }}
    .page {{ max-width: 820px; margin: 0 auto; padding: 4rem 2rem; }}
    .surface {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow-lg);
      padding: clamp(1.5rem, 5vw, 3.5rem);
    }}
    .brand-lockup {{
      display: flex; align-items: center; gap: 0.5rem;
      color: var(--muted); font-size: 0.82rem; margin: 0 0 1.5rem;
    }}
    .brand-mark {{ width: 18px; height: 18px; flex: none; }}
    .brand-name {{
      font-family: var(--font-mono); font-weight: 700;
      color: var(--text); letter-spacing: -0.02em;
    }}
    .brand-logo {{
      display: block; max-height: 72px; max-width: min(240px, 100%);
      object-fit: contain; margin: 0 0 1.5rem;
    }}
    .theme-header, .theme-footer {{ color: var(--muted); white-space: pre-wrap; }}
    .theme-header {{ margin: 0 0 1.75rem; }}
    .theme-footer {{ margin: 2rem 0 0; }}
    .document-body {{ color: var(--text); }}
    .document-body > * + * {{ margin-top: 1.5rem; }}
    .document-body :first-child {{ margin-top: 0; }}
    .document-body :last-child {{ margin-bottom: 0; }}
    .document-body h1, .document-body h2, .document-body h3, .document-body h4 {{
      font-family: var(--font-heading); line-height: 1.12; letter-spacing: -0.02em; font-weight: 650;
    }}
    .document-body h2 {{ font-size: 1.6rem; margin-top: 2.5rem; }}
    .document-body h3 {{ font-size: 1.25rem; margin-top: 2rem; }}
    .document-body a {{ color: var(--accent); text-decoration: underline; text-underline-offset: 2px; text-decoration-thickness: 1px; }}
    .document-body a:hover {{ text-decoration-thickness: 2px; }}
    .document-body ul, .document-body ol {{ padding-left: 1.3rem; }}
    .document-body li + li {{ margin-top: 0.4rem; }}
    .document-body strong {{ font-weight: 650; }}
    .document-body code {{ font: 500 0.88em/1.5 var(--font-mono); background: var(--surface-2); border: 1px solid var(--border); border-radius: 5px; padding: 0.1em 0.35em; }}
    .document-body pre {{ background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 1rem 1.1rem; overflow-x: auto; }}
    .document-body pre code {{ background: none; border: 0; padding: 0; }}
    .document-body blockquote {{ border-left: 3px solid var(--accent); color: var(--muted); margin-left: 0; padding-left: 1.5rem; }}
    .document-body hr {{ border: 0; border-top: 1px solid var(--border); margin: 2.5rem 0; }}
    .document-body table {{ width: 100%; border-collapse: collapse; font-size: 0.875rem; }}
    .document-body th, .document-body td {{ text-align: left; padding: 0.6rem 0.8rem; border-bottom: 1px solid var(--border); }}
    .document-body th {{ font-weight: 650; color: var(--muted); }}
  </style>
</head>
<body>
  <main class="page">
    <article class="surface">
{logo_html}      <p class="brand-lockup"><svg class="brand-mark" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><rect width="32" height="32" rx="7" fill="#b8482b"/><path d="M8 11.5 12 16 8 20.5" fill="none" stroke="#fffdf9" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/><line x1="15.5" y1="21" x2="23.5" y2="21" stroke="#fffdf9" stroke-width="2.4" stroke-linecap="round"/></svg>Presented with <span class="brand-name">atext</span></p>
{header_html}      <div class="document-body">
{content}
      </div>
{footer_html}    </article>
  </main>
</body>
</html>"""
