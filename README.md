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

Configuration is environment-driven:

- `ATEXT_DATABASE_URL` — PostgreSQL connection string.
- `ATEXT_AWID_REGISTRY_URL` — AWID registry URL, default `https://api.awid.ai`.
- `ATEXT_AUTH_CACHE_TTL_SECONDS` — AWID auth cache TTL, default `600`.
