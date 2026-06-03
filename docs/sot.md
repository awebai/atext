# atext Source of Truth

`atext` is the minimal text-sharing service for AWID-authenticated agent teams.
It is deliberately boring: plain text, append-only versions, and team-certificate
auth. Anything more complex must earn its way in from use.

## Product contract

A team has documents. A document is pure UTF-8 text plus append-only versions.
Each version records which authenticated agent created it.

V1 does **not** provide rich text, operational transform, CRDT sync, branches,
inline comments, document-level ACLs, or public sharing. The only permission
boundary is AWID team membership.

## Authority model

`atext` supports Bring Your Own Identity and Team (BYOIDT/BYOT):

- AWID is authoritative for namespaces, team public keys, team certificates,
  and certificate revocation.
- The customer/team controller signs team certificates. `atext` never receives
  or stores namespace-controller or team-controller private keys.
- Agents present their own identity signature plus a team certificate on every
  team-scoped request.
- `atext` verifies the request locally against cached AWID facts and fails
  closed when verification is indeterminate.

The service may cache public AWID facts for performance. The cache is not
product authority; AWID remains the source of truth.

## Authentication envelope

Every document endpoint requires team-certificate auth using the same shape as
`aweb` coordination endpoints:

```http
Authorization: DIDKey <did:key:z6Mk...> <base64url-no-padding-ed25519-signature>
X-AWEB-Timestamp: <RFC3339 UTC timestamp>
X-AWID-Team-Certificate: <base64-standard-json-team-certificate>
```

The signed request payload is canonical JSON:

```json
{"body_sha256":"<sha256 hex of request body>","team_id":"<team>:<namespace>","timestamp":"<RFC3339 UTC timestamp>"}
```

Verification steps:

1. Parse the DIDKey auth header and timestamp.
2. Reject timestamps outside the configured skew window (default 300s).
3. Compute `body_sha256` from the exact request bytes.
4. Verify the DIDKey signature over the canonical request payload.
5. Decode the team certificate.
6. Resolve the certificate's `team_id` to the team public key from AWID (cached).
7. Verify the certificate signature against the AWID-resolved team key, not
   against the `team_did_key` field by itself.
8. Check `certificate_id` against AWID revocation facts (cached).
9. Require `certificate.member_did_key == request.did_key`.
10. Build the request principal from the verified certificate.

If AWID is unavailable and no unexpired cache entry exists, the request fails
closed with 503/401. Never fall back to trusting a presented certificate without
an AWID-resolved team key.

## Minimal persisted state

`atext` stores only operational projections:

- `teams`: observed team id, cached team public key metadata, last-seen time.
- `agents`: observed team member identity (`team_id`, `did_key`, optional
  `did_aw`, optional `address`, alias, latest certificate id, last-seen time).
- `documents`: team-scoped document metadata.
- `document_versions`: append-only text versions with creator identity fields.

`atext` does not store raw private keys. It should not need to store raw team
certificates for v1. If later support workflows need certificate evidence, store
only explicit audit snapshots with a retention rule.

## Data model

### Team

- `team_id`: canonical AWID team id, `<name>:<namespace>`.
- `team_did_key`: AWID-resolved team public key used to verify certs.
- `first_seen_at`, `last_seen_at`.

### Agent

Scoped by `(team_id, did_key, alias)`:

- `did_key`: request signing identity.
- `did_aw`: stable identity when present.
- `address`: certificate-selected sender address when present.
- `alias`: team-local alias from the certificate.
- `latest_certificate_id`: latest observed cert id.
- `first_seen_at`, `last_seen_at`.

The same `did_aw` may appear in multiple teams. Do not collapse agent rows by
`did_aw` globally.

### Document

- `document_id`: UUID.
- `team_id`: owner team.
- `slug`: stable team-local document key.
- `title`: display title.
- `created_by_did_key`, optional `created_by_did_aw`, `created_by_alias`.
- timestamps.

`(team_id, slug)` is unique.

### Document version

- `version_id`: UUID.
- `document_id`.
- `version_number`: monotonically increasing integer per document.
- `body`: pure text.
- `created_by_did_key`, optional `created_by_did_aw`, optional address,
  alias, certificate id.
- `created_at`.

Versions are append-only. Fixes are new versions.

## API shape

Initial HTTP API:

- `POST /v1/documents` — create a document with initial body.
- `GET /v1/documents` — list documents for authenticated team.
- `GET /v1/documents/{slug}` — fetch current document for authenticated team.
- `GET /v1/documents/{slug}/versions` — list version metadata.
- `POST /v1/documents/{slug}/versions` — append a new text version.

All routes are scoped to the authenticated certificate's `team_id`. A request
must not name another team in the body and bypass this scope.

## Non-goals for v1

- No OAuth, API-key, or dashboard-auth write path.
- No hosted-controller authority. Hosted providers can proxy only if they sign
  as the agent identity and present a valid team certificate.
- No document-level permissions.
- No cross-team documents.
- No E2E encryption claim. Text stored in `atext` is server-readable unless a
  future client-side encryption layer is explicitly designed.

## Implementation notes

- Use `pgdbm` migrations with module name `atext`.
- Keep auth code small and explicit; prefer interop tests against aweb's
  certificate vectors before adding features.
- Deployed migrations are immutable. Recovery is a new forward migration.
