from __future__ import annotations

from pathlib import Path

from atext.presentation import render_presented_markdown


def test_render_presented_markdown_sanitizes_untrusted_html() -> None:
    html = render_presented_markdown(
        "# Hello\n\n<script>alert('x')</script>\n\n<img src=x onerror=alert(1)>\n\nA **safe** [link](https://example.com)."
    )

    assert "<h1>Hello</h1>" in html
    assert "<strong>safe</strong>" in html
    assert '<a href="https://example.com"' in html
    assert "<script" not in html.lower()
    assert "alert(" not in html
    assert "<img" not in html.lower()
    assert "onerror" not in html.lower()


def test_presentation_links_migration_is_document_version_bound() -> None:
    migration = (Path(__file__).resolve().parents[1] / "src" / "atext" / "migrations" / "003_presentation_links.sql").read_text()

    assert "CREATE TABLE IF NOT EXISTS {{tables.presentation_links}}" in migration
    assert "token TEXT PRIMARY KEY" in migration
    assert "document_id UUID NOT NULL REFERENCES {{tables.documents}}" in migration
    assert "version_number INTEGER NOT NULL" in migration
    assert "created_by_did_key TEXT NOT NULL" in migration
    assert "created_by_did_aw TEXT" in migration
    assert "created_by_alias TEXT NOT NULL" in migration
    assert "certificate_id TEXT NOT NULL" in migration
    assert "FOREIGN KEY (document_id, version_number) REFERENCES {{tables.document_versions}}" in migration
    assert "arti" + "fact" not in migration.lower()
