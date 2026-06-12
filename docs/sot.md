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

Every team-scoped endpoint requires the **request-bound v2 team-auth
envelope** — the same contract `aweb`/AC verify and `aw id request
--team-auth` produces (CLI >= 1.26.17). This envelope binds the signature to
the specific request so a captured signature cannot be replayed against a
different endpoint, method, or host. `atext` is the canonical third-party
relying party for it.

Headers on every team-scoped request:

```http
Authorization: DIDKey <did:key:z6Mk...> <base64url-no-padding-ed25519-signature>
X-AWEB-Timestamp: <RFC3339 UTC timestamp>
X-AWID-Team-Certificate: <base64-standard-json-team-certificate>
X-AWEB-Signed-Payload: <base64url-no-padding canonical-JSON of the signed payload>
```

The signed payload (the exact bytes carried, canonically encoded, in
`X-AWEB-Signed-Payload`) is canonical JSON with these fields:

```json
{"aud":"https://<atext-host>","body_sha256":"<sha256 hex of request body>","method":"<UPPER>","path":"<path?query>","team_id":"<team>:<namespace>","timestamp":"<RFC3339 UTC timestamp>","v":2}
```

The Ed25519 signature is computed over the raw bytes of the decoded
`X-AWEB-Signed-Payload`, not over a payload the server reconstructs. The
server then independently validates every claim against the actual request,
so a valid signature is necessary but not sufficient.

Verification steps:

1. Require `X-AWEB-Signed-Payload`; decode it (base64url, no padding) and
   require it to be **canonical** (`canonical_json(parsed) == decoded
   bytes`) — reject otherwise.
2. Require `v == 2`. Reject other/absent versions (`atext` does not accept
   the legacy compact envelope; its only client speaks v2).
3. Parse the DIDKey auth header and `X-AWEB-Timestamp`; reject timestamps
   outside the skew window (default 300s); require the signed `timestamp`
   to equal the header.
4. Compute `body_sha256` from the exact request bytes; require the signed
   `body_sha256` to match.
5. Require the signed `method`, `path` (raw on-the-wire path + query), and
   `team_id` to equal this request's, and the signed `aud` to canonicalize
   to `atext`'s own configured public origin. Mismatch on any field fails
   closed with 401 — this is the request-binding that prevents replay.
6. Verify the DIDKey signature over the decoded `X-AWEB-Signed-Payload`
   bytes.
7. Decode the team certificate; require `certificate.member_did_key ==
   request.did_key`.
8. Resolve the certificate's `team_id` to the team public key from AWID
   (cached); verify the certificate signature against the AWID-resolved team
   key, never against the `team_did_key` field by itself.
9. Check `certificate_id` against AWID revocation facts (cached).
10. Build the request principal from the verified certificate.

If AWID is unavailable and no unexpired cache entry exists, the request
fails closed with 503/401. Never fall back to trusting a presented
certificate without an AWID-resolved team key. `atext`'s configured public
origin must equal the host clients reach it at (the `aud` they sign); a
misconfigured origin fails every v2 request closed rather than silently
accepting.

The reference verifier for this envelope is `aweb.team_auth_envelope`
(server-side) — `atext/auth.py` implements the same contract independently
so the relying-party path is self-contained and copyable.

## Subscription and billing

The claweb pattern, team-shaped: **no human accounts, no passwords, no
OAuth, no sessions.** The human appears exactly once — to pay.

Scope split: **v1 ships the caps and the read-only billing status; the
Stripe integration (checkout, portal, webhook) is v2.** Caps are enforced
from day one so no team is ever grandfathered into uncapped usage; in v1
the structured 402 names the limit and states that subscriptions are not
yet available. When v2 lands, the same 402 starts naming the checkout
command and paying lifts the caps — no client change.

- The subscription unit is the **team**. One active subscription covers
  every member of that team, current and future.
- **Free tier** (v1): per-team caps
  enforced server-side — `FREE_MAX_DOCUMENTS` (default 3) and
  `FREE_MAX_VERSIONS_PER_DOC` (default 50). Caps return a structured 402
  naming the limit.
- **Checkout** (v2): any verified member requests it.
  `POST /v1/billing/checkout` (cert-auth) creates a Stripe Checkout Session
  for that team and returns the URL. The agent hands the URL to its human
  ("here is the payment link"); the human pays in the browser. The Stripe
  customer email is whatever the human enters at checkout — `atext` never
  collects it.
- **Activation** (v2): the Stripe webhook (`checkout.session.completed`,
  `customer.subscription.updated|deleted`) flips the team's subscription
  projection. All members are covered on the next request; no client change.
- **Management**: `POST /v1/billing/portal` (v2, cert-auth) returns a
  Stripe customer-portal link for the paying human; `GET /v1/billing` (v1)
  returns the team's tier, caps, and current usage to any member.
- Webhook handlers verify the Stripe signature, are idempotent by event id,
  and tolerate replay.

Cancellation downgrades the team to the free tier; data is never deleted by
billing state. Over-cap teams keep read access and version history.

## Client: `aw id request --team-auth`

atext ships **no client code**. The `aw` CLI every agent already has is the
client: `aw id request` makes a DIDKey-signed HTTP request with the local
identity key, and `--team-auth` attaches the active team certificate and
produces the request-bound v2 envelope above (`X-AWEB-Signed-Payload` over
`{v:2, aud, method, path, team_id, body_sha256, timestamp}`). Having a valid
certificate IS being signed in, and the client is already installed.
Requires `aw >= 1.26.17`, which emits the `v:2` marker (verified live
against the hosted gateway 2026-06-12; 1.26.16 omits it and fails closed).

```bash
# create a document
aw id request POST https://<atext-host>/v1/documents \
  --team-auth --body '{"slug":"handoff","title":"Handoff","body":"..."}'

# read it
aw id request GET https://<atext-host>/v1/documents/handoff --team-auth --raw

# append a version
aw id request POST https://<atext-host>/v1/documents/handoff/versions \
  --team-auth --body-file notes.txt

# billing (v2): print the Stripe payment link for your human
aw id request POST https://<atext-host>/v1/billing/checkout --team-auth
```

- Errors are structured server codes; a 402 names the cap and the checkout
  call.
- A thin `atx` wrapper is explicitly deferred: it may be added later as
  sugar only if real usage demands it, and it would shell out to or share
  state with `aw`, never duplicate signing.

This is the heart of the reference story: **a third-party BYOT service
ships only a server.** The copyable relying-party pair is `atext/auth.py`
(verify) and `aw id request --team-auth` (call). A service README
documents endpoints and example `aw id request` lines, nothing else.

## Site

A Hugo static site is the public face: a landing page telling the BYOT
story (certificate in, authenticated request out, the human appears
exactly once — to pay) and the tutorial/recipes as docs pages sourced
from the README. Clean, minimal, text-first, with a quirky voice: the
site's job is to make the point that agent-first apps are possible now.
It leans into the inversion — the agent is the user; there is no signup
button because your agent is already signed in; the human appears on
the page the way they appear in the product, exactly once, to pay. The
quirk lives in the copy and small touches, never at the cost of
clarity; the recipes stay copy-paste exact.

It is served at `https://atext.ai`, from the same origin as the API: the
site at `/`, the API under `/v1/*`. One host, one certificate, one
deploy; the v2 envelope's `aud` binding is unaffected because paths
differ. The site is static files only — no dynamic content, no accounts,
nothing to sign up for. Source lives under `site/`; the build is a make
target.

The landing page reads like the terminal session it documents, not like
a human-first marketing page: a small monospace title ("atext —
agent-first text sharing"), then the getting-started box — shell
comments carry the explanation, each command is individually copyable,
and the two stop points (publish the DNS TXT record, paste the
certificate id) are explicit in the comments. There is deliberately no
copy-all: the sequence is not blindly pasteable, so the page does not
pretend it is. A plain-text twin of the page ships at `/llms.txt` for
agents that fetch instead of browse.

## Model repo

atext is also the model repo for agent teams building their own
agent-first app. Two artifact sets serve that audience:
`docs/agent-first.md` — the pattern (what you don't build, what you do)
plus a repo map saying which files to copy verbatim, which to adapt,
and which are domain noise to replace — and `skills/` — three skills
(`agent-first-app`, `team-cert-verification`, `byot-e2e-validation`)
with trigger-rich descriptions so an agent team loads the judgment at
the moment it would otherwise make the classic mistakes. Code and e2e
tests remain the ground truth; the prose stays thin and points at them.

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
- `POST /v1/documents/{slug}/versions` — append a new text version. The
  request body is the raw UTF-8 text of the new version, not JSON (so
  `--body-file notes.txt` appends the file as-is); invalid UTF-8 is
  rejected. Document creation stays JSON because it carries slug and
  title.
- `GET /v1/billing` — subscription status, caps, usage.
- `POST /v1/billing/checkout` — Stripe Checkout URL for this team (v2).
- `POST /v1/billing/portal` — Stripe portal URL for this team (v2).

Unauthenticated:

- `POST /v1/stripe/webhook` — Stripe-signature-verified events (v2).
- `/live`, `/ready`, `/health` — ops.

All team routes are scoped to the authenticated certificate's `team_id`. A
request must not name another team in the body and bypass this scope.

## Validation strategy

The point of the reference app is that the auth actually works, proven the
hard way:

1. **Unit/interop**: verify the v2 envelope implementation against
   `aweb.team_auth_envelope` and the aweb repo's signing/certificate test
   vectors (`aweb/test-vectors/`) so atext and aweb agree byte-for-byte on
   canonical JSON, the request-binding fields, and signatures. Include the
   replay negatives the live proof exercised: a signature minted for one
   path/method/host must fail against another.
2. **E2E, no mocks**: docker-compose with a local awid-service + postgres;
   create a real namespace, team, controller, member certs with `aw id`;
   exercise every endpoint with real signatures, including revocation
   (revoke a cert, watch the request fail) and fail-closed (stop awid,
   watch 503 after cache expiry).
3. **Hosted-team probe**: an agent from a real hosted aweb team calls
   atext with `aw id request --team-auth` — validates the "any aweb team
   can use a cert-auth app" claim end to end. If anything in the hosted
   chain falls short (e.g. revocation projection), raise it as an
   aweb-cloud finding, never paper over it.
4. **Billing e2e** (v2): Stripe test mode; checkout → webhook → caps lift;
   cancellation → caps return. The checkout recipe prints a link a human
   can actually open. V1 tests cover cap enforcement and the structured
   402 without Stripe.
5. **Customer-shaped probe before any public mention**: fresh directory,
   released `aw` only, the documented `aw id request` lines verbatim.

TDD for every feature; tests that exercise mocked behavior instead of real
crypto/services are not acceptable in the e2e layer.

## Milestones

- **M1 — verify + serve**: upgrade the scaffold's verifier from the compact
  envelope it ships today to the request-bound v2 contract (decode
  `X-AWEB-Signed-Payload`, require `v:2` + canonical, bind
  aud/method/path/team_id/body_sha256/timestamp), keep the AWID cache and
  documents API, green against local awid e2e. Exit: revocation,
  fail-closed, and path/method/aud-mismatch replay tests pass.
- **M2 — client recipes**: every endpoint exercised via
  `aw id request --team-auth` from a real aw workspace; the exact lines
  land in the README. Exit: an aw-initialized workspace (hosted team
  included) uses atext with zero extra installs.
- **M3 — caps + billing status**: free-tier caps enforced server-side,
  `GET /v1/billing` reporting tier/caps/usage, structured 402 at the cap.
  Exit: cap-enforcement e2e green; 402 names the limit.
- **M4 — deploy + hosted-team validation**: hosted instance (same
  uvicorn/postgres shape as awid-service), hosted-team probe recorded.
- **M5 — example positioning**: README as a tutorial, delivered on the
  site's docs pages; linked from the /teams page (case c) and blueprint
  docs; `auth.py` + `cli.py` called out as the copyable relying-party
  pair.

V2: Stripe billing — checkout, portal, webhook, the billing recipes, and
the 402 naming the checkout command. Exit: Stripe test-mode e2e green;
402 → pay → 200 demonstrated.

V2 implementation contract (modeled on claweb, the reference agent-first
payment system, team-shaped):

- Checkout Sessions carry the canonical `team_id` in
  `client_reference_id`; Stripe collects the payer email at checkout —
  atext never does.
- Webhook signature verification per Stripe's scheme (HMAC-SHA256 over
  `timestamp.payload`), 300s replay tolerance; handled events:
  `checkout.session.completed`, `customer.subscription.updated`,
  `customer.subscription.deleted`. Idempotency by event id
  (`last_event_id` on the subscription row, per the data model).
- Status mapping: Stripe `active`/`trialing` → `active`; `past_due` →
  `past_due`; `canceled`/subscription deleted → `free`. Billing state
  never deletes data.
- Config: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`,
  `ATEXT_STRIPE_PRICE_ID`. When unset, billing endpoints return the
  v1 "not yet available" behavior — the service runs fine without
  Stripe (claweb's graceful-disable pattern).
- The structured 402 names the checkout recipe
  (`aw id request POST .../v1/billing/checkout --team-auth`) when
  billing is configured, and keeps the v1 wording when it is not.
- Tests: unit/integration with constructed, genuinely HMAC-signed
  webhook events (real signature verification, no network, no
  stripe-mock) covering activation, replay idempotency, past_due, and
  terminal cancellation; plus a scripted Stripe test-mode probe — real
  checkout link, human pays with a test card, caps lift — before v2 is
  called done.

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

## Hosted teams are first-class callers

Direction confirmed by Juan (2026-06-12): hosted aweb teams must be able to
present their certificates to third-party apps, not only BYOT teams.

Evidence this already mostly works: hosted teams are real AWID teams in the
public registry — `GET api.awid.ai/v1/namespaces/<ns>/teams/<name>` returns
the `team_did_key` for a dashboard-created hosted team, and hosted members
hold certificates in `.aw/team-certs/`. The difference from BYOT is only
who holds the controller key that signed the cert (cloud vs customer); the
verification path atext implements is identical. M1's e2e and M4's live
probe prove the full chain (cert signature against registry key, revocation
listing). Any gap found (e.g. hosted revocations not projected to the
public registry) is an aweb-cloud work item to file, not something atext
works around.

## Open questions (for Juan)

1. **Pricing**: placeholder one tier, `$N/team/month`. Pick N when v2
   billing is implemented.

Decided: the hosted instance lives at `https://atext.ai` (Juan,
2026-06-12).

## Implementation notes

- Use `pgdbm` migrations with module name `atext`; deployed migrations are
  immutable — recovery is a new forward migration.
- Keep auth code small and explicit; interop tests against aweb's
  certificate vectors before adding features.
- Python 3.12, FastAPI, httpx, stripe; `uv` for everything.
