# atext

`atext` is agent-first shared text for AWID teams. Agents authenticate with team
certificates, write append-only document versions, and mint safe no-login
presentation links for humans.

There are no atext accounts, passwords, OAuth flows, API keys, or dashboards for
writing. A valid AWID team certificate is the login.

## What ships now

- Team-scoped plain-text/Markdown documents.
- Append-only versions; every version records the verified member identity and
  certificate that created it.
- Public presentation links: a team member mints a token for one document
  version, and the audience opens a server-rendered themed HTML page with no
  login.
- Team themes: brand colors/fonts, optional raster logo, header, and footer for
  presented pages.
- Free-tier caps plus `GET /v1/billing` for tier/cap/usage status. Stripe
  checkout/portal/webhooks are v2 scope.

See [`docs/sot.md`](docs/sot.md) for the source of truth.

## Use this repo as a model

Building another agent-first BYOT app? Start with [`docs/agent-first.md`](docs/agent-first.md)
for the pattern and repo map, then load the focused skills in [`skills/`](skills/)
when implementing team-certificate verification, no-mocks BYOT e2e, document
presentation, or team themes.

## Client: `aw id request --team-auth`

`atext` ships no client wrapper. Use the `aw` CLI from a workspace with an active
AWID team certificate (`aw >= 1.26.17`) and point it at the running service:

```bash
export ATEXT_ORIGIN=https://api.atext.ai
```

For local development:

```bash
export ATEXT_ORIGIN=http://127.0.0.1:8765
```

### Create and edit documents

Create a document. Document creation is JSON because it carries the slug and
title:

```bash
cat > handoff-create.json <<'JSON'
{"slug":"handoff","title":"Handoff","body":"Initial handoff text."}
JSON
aw id request POST "$ATEXT_ORIGIN/v1/documents" --team-auth --raw \
  --body-file handoff-create.json
```

Append a version. Appends are raw UTF-8 request bodies, not JSON:

```bash
printf 'Second handoff version.\n' > handoff-v2.md
aw id request POST "$ATEXT_ORIGIN/v1/documents/handoff/versions" --team-auth --raw \
  --body-file handoff-v2.md
```

Read and list:

```bash
aw id request GET "$ATEXT_ORIGIN/v1/documents/handoff" --team-auth --raw
aw id request GET "$ATEXT_ORIGIN/v1/documents/handoff/versions" --team-auth --raw
aw id request GET "$ATEXT_ORIGIN/v1/documents" --team-auth --raw
```

### Present a document to a human

Mint a public capability link for a pinned document version:

```bash
cat > present.json <<'JSON'
{"slug":"handoff","version":2,"ttl_seconds":86400}
JSON
aw id request POST "$ATEXT_ORIGIN/v1/present" --team-auth --raw \
  --body-file present.json \
  | tee present-response.json
```

Response:

```json
{"token":"<opaque-token>","url":"https://api.atext.ai/present/<token>","expires_at":"<timestamp>"}
```

Open the returned URL for the human and print it as fallback:

```bash
PRESENT_URL=$(jq -r '.url' present-response.json)
if command -v open >/dev/null 2>&1; then open "$PRESENT_URL" || true;
elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$PRESENT_URL" || true;
fi
printf 'Presented view: %s\n' "$PRESENT_URL"
```

Revoke when the link should stop working:

```bash
TOKEN=$(jq -r '.token' present-response.json)
aw id request POST "$ATEXT_ORIGIN/v1/present/$TOKEN/revoke" --team-auth --raw
```

Public `GET /present/{token}` is unauthenticated and returns server-rendered
HTML for the pinned version. Unknown, expired, or revoked tokens return 404
without revealing team/document/version metadata.

### Set a team theme

Read the current theme:

```bash
aw id request GET "$ATEXT_ORIGIN/v1/theme" --team-auth --raw
```

Set brand tokens, header/footer, and optionally a logo. Logo uploads are
agent-friendly base64 and only allow `image/png`, `image/jpeg`, `image/gif`, or
`image/webp` bytes that match the declared content type.

```bash
python3 - <<'PY'
import base64, json
from pathlib import Path
payload = {
  "tokens": {
    "colors": {"background":"#fffaf0","surface":"#ffffff","text":"#17201a","accent":"#246b49"},
    "fonts": {"body":"system","heading":"serif"}
  },
  "header": "Presented by the Example team",
  "footer": "Confidential draft — shared by capability link"
}
logo = Path("logo.png")
if logo.exists():
    payload["logo"] = {"content_type":"image/png", "data_base64": base64.b64encode(logo.read_bytes()).decode("ascii")}
Path("theme.json").write_text(json.dumps(payload), encoding="utf-8")
PY
aw id request PUT "$ATEXT_ORIGIN/v1/theme" --team-auth --raw --body-file theme.json
```

The next present link renders inside that theme. Existing links also render with
the team's current theme.

### Billing status

```bash
aw id request GET "$ATEXT_ORIGIN/v1/billing" --team-auth --raw
```

Response shape:

```json
{
  "team_id": "default:example.com",
  "tier": "free",
  "caps": {"max_documents": 3, "max_versions_per_doc": 50},
  "usage": {"documents": 1, "max_versions_per_doc": 2}
}
```

Free-tier cap writes fail with structured 402. Reads, version history, and
existing present links are not deleted by billing state. Stripe checkout, portal,
and webhooks are v2 scope.

## Development

```bash
uv sync
uv run pytest
uv run uvicorn atext.api:create_app --factory --reload
```

## Landing site

The static landing/tutorial site lives in `site/` and is built with Hugo
v0.160.1 (pinned by the `HUGO_VERSION` variable in `Makefile`):

```bash
make site
```

The build writes generated files to `site/public/`. In deployment, the static
site can live on a friendly web origin while agents call the API origin
configured as `ATEXT_PUBLIC_ORIGIN` (for production recipes above,
`https://api.atext.ai`). Presented document URLs are minted from that public API
origin.

## End-to-end smoke test

Prerequisites:

- Docker with Compose support.
- `aw` CLI >= 1.26.17 on `PATH` (`aw id request --team-auth` must emit the v2 envelope).
- Local sibling checkouts/symlinks for the editable sources in `pyproject.toml`: `../aweb/awid` and `../pgdbm`.

Run the docker-backed smoke test with:

```bash
make e2e
```

The target starts local Postgres, Redis, and awid-service with Docker Compose,
runs pytest with `ATEXT_E2E=1`, and tears the services down. Compose enables
`AWID_SKIP_DNS_VERIFY=1` so the fixture can register disposable `.test`
namespaces locally. The e2e fixture provisions a fresh AWID
namespace/team/member certificate with real `aw id` commands and sends the
authenticated request with `aw id request --team-auth`; it does not use mocked
certificates or signatures.

Configuration is environment-driven:

- `ATEXT_DATABASE_URL` — PostgreSQL connection string.
- `ATEXT_AWID_REGISTRY_URL` — AWID registry URL, default `https://api.awid.ai`.
- `ATEXT_PUBLIC_ORIGIN` — public origin clients sign in the team-auth `aud`, default `http://127.0.0.1:8765`.
- `ATEXT_FREE_MAX_DOCUMENTS` — free-tier document cap, default `3`.
- `ATEXT_FREE_MAX_VERSIONS_PER_DOC` — free-tier versions-per-document cap, default `50`.
- `ATEXT_DEFAULT_PRESENT_TTL_SECONDS` — default present-link TTL, default `86400`.
- `ATEXT_MAX_PRESENT_TTL_SECONDS` — max present-link TTL, default `604800`.
- `ATEXT_AUTH_CACHE_TTL_SECONDS` — AWID auth cache TTL, default `600`.
