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

## Development

```bash
uv sync
uv run pytest
uv run uvicorn atext.api:create_app --factory --reload
```

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
- `ATEXT_AUTH_CACHE_TTL_SECONDS` — AWID auth cache TTL, default `600`.
