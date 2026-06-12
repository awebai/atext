# atext Source of Truth

`atext` is the **reference BYOT agent-first application**: the smallest
non-trivial service where agents authenticate by presenting an AWID team
certificate. One team member gets the team subscribed; every member can use
it. It is deliberately boring: plain text, append-only versions,
team-certificate auth, one team-level subscription. Anything more complex
must earn its way in from use.

## Why this app

The reference app has one job: prove the BYOT promise end to end with the
least possible domain noise. Shared team text fits because:

- the domain is minimal but real — agent teams genuinely need durable shared
  text (handoffs, notes, drafts) that outlives any single workspace and
  isn't a git repo;
- every write is attributed to a verified member identity, so the app
  exercises the full auth texture: per-request signatures, certificate
  verification, revocation, team scoping;
- "one member subscribes, all members use it" maps exactly onto team-level
  billing, the second half of the BYOT story;
- nothing in it duplicates aweb itself (a task board would) and nothing in
  it adds infrastructure noise (file storage would).

Rejected alternatives: URL shortener (trivial, no identity texture), task
board (duplicates aweb coordination), file/blob store (storage complexity
swamps the auth lesson).

## Product contract

A team has documents. A document is pure UTF-8 text plus append-only
versions. Each version records which authenticated agent created it.

V1 does **not** provide rich text, operational transform, CRDT sync,
branches, inline comments, document-level ACLs, or public sharing. The only
permission boundary is AWID team membership; the only billing boundary is
the team subscription.

## Authority model

`atext` is a relying party. It supports Bring Your Own Identity and Team
(BYOIDT/BYOT) and, by the same mechanism, hosted aweb teams whose members
hold team certificates:

- AWID is authoritative for namespaces, team public keys, team
  certificates, and certificate revocation.
- The team controller (customer-held for BYOT, cloud-held for hosted teams)
  signs team certificates. `atext` never receives or stores
  namespace-controller or team-controller private keys.
- Agents present their own identity signature plus a team certificate on
  every team-scoped request.
- `atext` verifies the request locally against cached AWID facts and fails
  closed when verification is indeterminate.
- Stripe is authoritative for payment state; `atext` stores only the
  subscription projection.

The service may cache public AWID facts for performance. The cache is not
product authority; AWID remains the source of truth.

## Authentication envelope

Every team-scoped endpoint requires team-certificate auth using the same
shape as `aweb` coordination endpoints:

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
6. Resolve the certificate's `team_id` to the team public key from AWID
   (cached).
7. Verify the certificate signature against the AWID-resolved team key, not
   against the `team_did_key` field by itself.
8. Check `certificate_id` against AWID revocation facts (cached).
9. Require `certificate.member_did_key == request.did_key`.
10. Build the request principal from the verified certificate.

If AWID is unavailable and no unexpired cache entry exists, the request
fails closed with 503/401. Never fall back to trusting a presented
certificate without an AWID-resolved team key.

## Subscription and billing

The claweb pattern, team-shaped: **no human accounts, no passwords, no
OAuth, no sessions.** The human appears exactly once — to pay.

- The subscription unit is the **team**. One active subscription covers
  every member of that team, current and future.
- **Free tier** (so the whole flow works before any payment): per-team caps
  enforced server-side — `FREE_MAX_DOCUMENTS` (default 3) and
  `FREE_MAX_VERSIONS_PER_DOC` (default 50). Caps return a structured 402
  naming the limit and the checkout command.
- **Checkout**: any verified member requests it.
  `POST /v1/billing/checkout` (cert-auth) creates a Stripe Checkout Session
  for that team and returns the URL. The agent hands the URL to its human
  ("here is the payment link"); the human pays in the browser. The Stripe
  customer email is whatever the human enters at checkout — `atext` never
  collects it.
- **Activation**: the Stripe webhook (`checkout.session.completed`,
  `customer.subscription.updated|deleted`) flips the team's subscription
  projection. All members are covered on the next request; no client change.
- **Management**: `POST /v1/billing/portal` (cert-auth) returns a Stripe
  customer-portal link for the paying human; `GET /v1/billing` returns the
  team's tier, caps, and current usage to any member.
- Webhook handlers verify the Stripe signature, are idempotent by event id,
  and tolerate replay.

Cancellation downgrades the team to the free tier; data is never deleted by
billing state. Over-cap teams keep read access and version history.

## Agent CLI: `atx`

The CLI is how agents actually use the service, and it must require **zero
new setup** in an aweb workspace: `atx` reads the same `.aw/` state `aw`
created — the signing key and the active team certificate — and signs the
envelope with them. Having a valid certificate IS being signed in.

```bash
atx docs list
atx docs get <slug>
atx docs put <slug> [--title T] [--file F | --body B | -]   # create or append version
atx docs history <slug>
atx billing                  # tier, caps, usage
atx billing checkout         # print the Stripe payment link for your human
atx billing portal           # print the management link for your human
```

- `atx` is a small Python package (same repo, `atext.cli`), installed with
  `uv tool install atext` or `uvx atext`.
- `--service <url>` / `ATEXT_URL` selects the deployment; default is the
  hosted instance.
- Errors surface the structured server codes verbatim; a 402 prints the
  checkout hint.
- No interactive prompts: every command is agent-safe.

The CLI doubles as the **client reference implementation**: a third party
building their own BYOT app copies `atext/cli.py` + `atext/auth.py` as the
canonical relying-party pair.

## Data model

### Team

- `team_id`: canonical AWID team id, `<name>:<namespace>`.
- `team_did_key`: AWID-resolved team public key used to verify certs.
- `first_seen_at`, `last_seen_at`.

### Subscription (new)

One row per team:

- `team_id` (unique), `tier` (`free` | `active` | `past_due`),
- `stripe_customer_id`, `stripe_subscription_id` (nullable),
- `current_period_end`, `updated_at`,
- `last_event_id` (webhook idempotency).

### Agent

Scoped by `(team_id, did_key, alias)`:

- `did_key`: request signing identity.
- `did_aw`: stable identity when present.
- `address`: certificate-selected sender address when present.
- `alias`: team-local alias from the certificate.
- `latest_certificate_id`: latest observed cert id.
- `first_seen_at`, `last_seen_at`.

The same `did_aw` may appear in multiple teams. Do not collapse agent rows
by `did_aw` globally.

### Document

- `document_id`: UUID; `team_id`: owner team; `slug` (unique per team);
  `title`; `created_by_did_key`, optional `created_by_did_aw`,
  `created_by_alias`; timestamps.

### Document version

- `version_id`, `document_id`, `version_number` (monotonic per document),
  `body` (pure text), creator identity fields (`did_key`, optional
  `did_aw`, address, alias, certificate id), `created_at`.

Versions are append-only. Fixes are new versions.

## API shape

Team-scoped (cert-auth):

- `POST /v1/documents` — create a document with initial body.
- `GET /v1/documents` — list documents for the authenticated team.
- `GET /v1/documents/{slug}` — fetch current version.
- `GET /v1/documents/{slug}/versions` — list version metadata.
- `POST /v1/documents/{slug}/versions` — append a new text version.
- `GET /v1/billing` — subscription status, caps, usage.
- `POST /v1/billing/checkout` — Stripe Checkout URL for this team.
- `POST /v1/billing/portal` — Stripe portal URL for this team.

Unauthenticated:

- `POST /v1/stripe/webhook` — Stripe-signature-verified events.
- `/live`, `/ready`, `/health` — ops.

All team routes are scoped to the authenticated certificate's `team_id`. A
request must not name another team in the body and bypass this scope.

## Validation strategy

The point of the reference app is that the auth actually works, proven the
hard way:

1. **Unit/interop**: verify the envelope implementation against the aweb
   repo's signing/certificate test vectors (`aweb/test-vectors/`) so atext
   and aweb agree byte-for-byte on canonical JSON and signatures.
2. **E2E, no mocks**: docker-compose with a local awid-service + postgres;
   create a real namespace, team, controller, member certs with `aw id`;
   exercise every endpoint with real signatures, including revocation
   (revoke a cert, watch the request fail) and fail-closed (stop awid,
   watch 503 after cache expiry).
3. **Hosted-team probe**: an agent from a real hosted aweb team uses its
   fetched team certificate against atext — validates the "any aweb team
   can use a cert-auth app" claim. If hosted certs cannot satisfy the
   envelope today, that is a product finding to raise, not to paper over.
4. **Billing e2e**: Stripe test mode; checkout → webhook → caps lift;
   cancellation → caps return. CLI prints links a human can actually open.
5. **Customer-shaped probe before any public mention**: fresh directory,
   released `aw` + `uvx atext`, the documented commands verbatim.

TDD for every feature; tests that exercise mocked behavior instead of real
crypto/services are not acceptable in the e2e layer.

## Milestones

- **M1 — verify + serve**: auth envelope + AWID cache + documents API
  green against local awid e2e (the existing scaffold, finished and
  proven). Exit: revocation and fail-closed tests pass.
- **M2 — `atx` CLI**: reads `.aw/`, all docs commands, structured errors.
  Exit: an aw-initialized workspace uses atext with zero extra setup.
- **M3 — billing**: free-tier caps, checkout/portal/webhook, `atx billing`.
  Exit: Stripe test-mode e2e green; 402 → pay → 200 demonstrated.
- **M4 — deploy + hosted-team validation**: hosted instance (same
  uvicorn/postgres shape as awid-service), hosted-team probe recorded.
- **M5 — example positioning**: README as a tutorial; linked from the
  /teams page (case c) and blueprint docs; `auth.py` + `cli.py` called out
  as the copyable relying-party pair.

Build note: this is a good candidate for a blueprint-created team to build
(dogfood: the team that builds the BYOT example is itself created from a
blueprint).

## Non-goals for v1

- No OAuth, API-key, password, or dashboard-auth write path.
- No hosted-controller authority inside atext. Hosted providers can proxy
  only if they sign as the agent identity and present a valid team
  certificate.
- No per-seat billing, metered billing, or invoices beyond what Stripe's
  portal provides.
- No document-level permissions, cross-team documents, or public sharing.
- No E2E encryption claim. Text stored in `atext` is server-readable unless
  a future client-side encryption layer is explicitly designed.

## Open questions (for Juan)

1. **Hosted-team certificates**: confirmed direction that hosted aweb teams
   should be able to present certs to third-party apps? M4 validates it;
   if cloud-held controllers don't currently mint member certs agents can
   fetch, that becomes an aweb-cloud work item.
2. **Pricing**: placeholder one tier, `$N/team/month`. Pick N at M3.
3. **Name/domain for the hosted instance** (atext.aweb.ai?). Needed at M4.

## Implementation notes

- Use `pgdbm` migrations with module name `atext`; deployed migrations are
  immutable — recovery is a new forward migration.
- Keep auth code small and explicit; interop tests against aweb's
  certificate vectors before adding features.
- Python 3.12, FastAPI, httpx, stripe; `uv` for everything.
