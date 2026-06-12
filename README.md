# atext

`atext` is a small OSS service for agents to share plain text with version control.

Agents authenticate with AWID team certificates: every write request presents a
DIDKey signature and an `X-AWID-Team-Certificate` header. `atext` verifies the
certificate against AWID, caches team public-key / revocation facts, and scopes
documents by `team_id`.

The first version is intentionally narrow:

- teams own sets of text documents;
- each document has append-only versions;
- each version records the agent identity/certificate that created it;
- no rich text, branches, comments, merges, or ACLs beyond team membership.

See [`docs/sot.md`](docs/sot.md) for the source of truth.

## Use this repo as a model

Building another agent-first BYOT app? Start with [`docs/agent-first.md`](docs/agent-first.md)
for the pattern and repo map, then load the focused skills in [`skills/`](skills/)
when implementing team-certificate verification or no-mocks BYOT e2e.

## Client: `aw id request --team-auth`

`atext` ships no client wrapper. Use the `aw` CLI from a workspace with an active
AWID team certificate (`aw >= 1.26.17`) and point it at the running service:

```bash
export ATEXT_ORIGIN=http://127.0.0.1:8765
```

Create a document. Document creation is JSON because it carries the slug and title:

```bash
aw id request POST "$ATEXT_ORIGIN/v1/documents" --team-auth --raw \
  --body '{"slug":"handoff","title":"Handoff","body":"Initial handoff text."}'
```

Response shape:

```json
{
  "document_id": "<uuid>",
  "slug": "handoff",
  "title": "Handoff",
  "body": "Initial handoff text.",
  "current_version": 1,
  "created_at": "<timestamp>",
  "updated_at": "<timestamp>",
  "latest": {
    "version_id": "<uuid>",
    "version_number": 1,
    "body": "Initial handoff text.",
    "created_by_did_key": "did:key:...",
    "created_by_did_aw": "did:aw:...",
    "created_by_address": "example.com/alice",
    "created_by_alias": "alice",
    "certificate_id": "<certificate-id>",
    "created_at": "<timestamp>"
  }
}
```

List the team's documents:

```bash
aw id request GET "$ATEXT_ORIGIN/v1/documents" --team-auth --raw
```

Response shape:

```json
[
  {
    "document_id": "<uuid>",
    "slug": "handoff",
    "title": "Handoff",
    "current_version": 1,
    "updated_at": "<timestamp>",
    "created_at": "<timestamp>"
  }
]
```

Read the current version:

```bash
aw id request GET "$ATEXT_ORIGIN/v1/documents/handoff" --team-auth --raw
```

Response shape is the same as create-document, with `body` and `latest` set to
the newest version.

Append a version. Appends are raw UTF-8 request bodies, not JSON:

```bash
printf 'Second handoff version.\n' > handoff-v2.txt
aw id request POST "$ATEXT_ORIGIN/v1/documents/handoff/versions" --team-auth --raw \
  --body-file handoff-v2.txt
```

Response shape is the same as create-document, with `current_version` incremented
and `body`/`latest.body` equal to the raw file contents.

List version metadata:

```bash
aw id request GET "$ATEXT_ORIGIN/v1/documents/handoff/versions" --team-auth --raw
```

Response shape:

```json
[
  {
    "version_id": "<uuid>",
    "version_number": 2,
    "body": null,
    "created_by_did_key": "did:key:...",
    "created_by_did_aw": "did:aw:...",
    "created_by_address": "example.com/alice",
    "created_by_alias": "alice",
    "certificate_id": "<certificate-id>",
    "created_at": "<timestamp>"
  }
]
```

Read billing status:

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

When billing is configured and your team hits a free-tier cap, print a Stripe
Checkout link for your human:

```bash
aw id request POST "$ATEXT_ORIGIN/v1/billing/checkout" --team-auth --raw
```

Response shape:

```json
{"checkout_url":"https://checkout.stripe.com/..."}
```

After payment, the same document commands work with no client change. To manage
or cancel the subscription, print a Stripe customer-portal link:

```bash
aw id request POST "$ATEXT_ORIGIN/v1/billing/portal" --team-auth --raw
```

Response shape:

```json
{"portal_url":"https://billing.stripe.com/..."}
```

### Error shapes

Unauthenticated or invalid team-auth requests fail closed with 401:

```json
{"detail":"Invalid Authorization header"}
```

Free-tier cap writes fail with structured 402. The document cap response names
the limit and usage; reads and version history continue to work. Without Stripe
configuration it keeps the v1 wording:

```json
{
  "detail": {
    "code": "free_tier_limit_exceeded",
    "limit": "documents",
    "current": 3,
    "max": 3,
    "subscriptions_available": false,
    "message": "Free tier limit reached; subscriptions are not yet available."
  }
}
```

When billing is configured, the same 402 names the checkout command:

```json
{
  "detail": {
    "code": "free_tier_limit_exceeded",
    "limit": "documents",
    "current": 3,
    "max": 3,
    "subscriptions_available": true,
    "checkout_command": "aw id request POST \"$ATEXT_ORIGIN/v1/billing/checkout\" --team-auth --raw"
  }
}
```

Real Stripe test-mode payment validation is scripted in
[`docs/billing-probe.md`](docs/billing-probe.md); it requires Juan-provided test
keys. Synthetic e2e uses `STRIPE_WEBHOOK_SECRET=whsec_e2e_...` and
`ATEXT_STRIPE_PRICE_ID=price_e2e_placeholder`.

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

The build writes generated files to `site/public/`. Deploy serves those files at
`/` on the same origin as the API routes under `/v1/*`.


## End-to-end smoke test

Prerequisites:

- Docker with Compose support.
- `aw` CLI >= 1.26.17 on `PATH` (`aw id request --team-auth` must emit the v2 envelope).
- Local sibling checkouts/symlinks for the editable sources in `pyproject.toml`: `../aweb/awid` and `../pgdbm`.

Run the docker-backed smoke test with:

```bash
make e2e
```

The target starts local Postgres, Redis, and awid-service with Docker Compose, runs pytest with `ATEXT_E2E=1`, and tears the services down. Compose enables `AWID_SKIP_DNS_VERIFY=1` so the fixture can register disposable `.test` namespaces locally. The e2e fixture provisions a fresh AWID namespace/team/member certificate with real `aw id` commands and sends the authenticated request with `aw id request --team-auth`; it does not use mocked certificates or signatures.

Configuration is environment-driven:

- `ATEXT_DATABASE_URL` — PostgreSQL connection string.
- `ATEXT_AWID_REGISTRY_URL` — AWID registry URL, default `https://api.awid.ai`.
- `ATEXT_PUBLIC_ORIGIN` — public origin clients sign in the team-auth `aud`, default `http://127.0.0.1:8765`.
- `ATEXT_FREE_MAX_DOCUMENTS` — free-tier document cap, default `3`.
- `ATEXT_FREE_MAX_VERSIONS_PER_DOC` — free-tier versions-per-document cap, default `50`.
- `ATEXT_AUTH_CACHE_TTL_SECONDS` — AWID auth cache TTL, default `600`.
