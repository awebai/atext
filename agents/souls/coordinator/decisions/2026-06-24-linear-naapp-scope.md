# Linear naapp — scope

Date: 2026-06-24. Author: coordinator. Status: proposed scope (cloud-side sections
pending aw-coordinator validation; product decisions pending Juan).

Grounded in research (sourced, 2026-06-24): Linear MCP + OAuth actor/attribution +
OAuth scopes/webhooks/rate-limits (linear.app/developers), and a code read of the
ac/aweb-cloud gateway + connector-grant + auth-bridge.

## 1. Thesis

A first-party **Linear naapp**: it holds a team's Linear connection server-side and
exposes Linear as native `aw linear …` verbs via its manifest. Team members use
Linear through their **existing AWID team cert** — no per-agent MCP setup, no
per-agent Linear credential. The value over per-agent MCP: credential **custody**
(token server-side, rotate/revoke once), **unified identity** (one cert, all apps),
**team governance** (entitlements/budgets/role policy), and a **signed per-member
audit trail** — i.e. per-member accountability *without* distributing a Linear
credential to every agent.

## 2. The attribution model (the crux)

Linear's two real options (verified against Linear's schema + OAuth-actor docs):

- **actor=user** — genuine Linear-user actor (real attribution + that user's
  permissions), but requires EACH member to OAuth-authorize → N tokens, one per
  member. Not "one connection per team."
- **actor=app** — one team token; every mutation's actor is the **bot**
  (`creator=null`, `botActor=app`). `createAsUser` is a **String name** (+avatar),
  NOT a Linear user — surfaced as `ActorBot.userDisplayName` / "external user on
  behalf of whom the bot acted" / "Name (via App)". Cosmetic: no permissions, not
  that user's activity.

**Decision (default): actor=app + aweb-layer attribution.** One team connection;
Linear shows the app bot + an optional cosmetic per-member label. The REAL
accountability is at the aweb layer: every `aw linear` call is signed with the
member's AWID DID, recorded by the naapp/gateway → a tamper-evident who-did-what
record independent of Linear. **Optional Phase 3:** per-member OAuth (actor=user)
for teams needing Linear-native per-person attribution.

## 3. Architecture (how it fits aweb)

- **Linear naapp** = a hosted aweb app (like library/folio): an `aweb-app.json`
  manifest exposing `aw linear` verbs, a service that brokers to Linear's GraphQL
  API, AWID team-cert auth per call. Built on the aweb-naapp toolkit.
- **Connector grant** holds the team's Linear OAuth token server-side. The
  aweb-cloud connector-grant table is *designed* for external `oauth` bindings
  (binding_method enum incl. `oauth`/`service_account`; issuer/jwks_uri/subject_pattern
  columns) but today only has MCP-OAuth + API-key adapters — **a Linear adapter is
  net-new.**
- **Gateway** composes the manifest verbs + must carry the **member DID** downstream.
  The composition gateway exists but is **shadow/not-live** (a called-out
  "flip-the-stub" step); today its signed payload carries `team_id` only (no member).
- **Per-member attribution path:** member's team cert → naapp authenticates the
  member (their AWID DID; the auth bridge already mints per-(team,member) custodial
  DID actors today for mail/chat/tasks) → naapp brokers to Linear with the team
  token (actor=app), optionally passing `createAsUser=<member display name>` →
  records the member DID in the aweb audit/usage log.
- **Events (Linear → aweb):** the naapp subscribes to Linear webhooks per team and
  emits aweb events (e.g. `linear/issue.assigned` wakes the assigned agent,
  `linear/comment.created`). Linear webhook payloads include the `actor` (User /
  OauthClient / Integration), so we can map back to the member when known.

## 4. Linear connection details (sourced)

- **OAuth app:** ONE global Linear OAuth app (we register at
  linear.app/settings/api/applications/new). Confirmed multi-tenant: "one OAuth
  application can be installed across multiple workspaces … a unique ID for each
  workspace." Each aweb team's Linear-workspace **admin** installs it (actor=app
  requires admin to complete the workspace-scoped install).
- **Scopes:** `read` (broad read of issues/projects/teams/users), `issues:create`,
  `comments:create`, and `write` (needed for issue UPDATE — there is no
  `issues:update` scope). NOT `admin` (actor=app cannot request admin).
- **Token:** authorization-code install → 24h access token + **refresh token**
  (persistent; the naapp must refresh reliably). (Alternative client-credentials
  app token = 30 days, no refresh, capped 1000 — rejected for a long-lived server.)
- **Rate limits:** 5,000 req/hr + 2,000,000 complexity pts/hr per app-user, and
  Linear "dynamically increase[s] rate limits for workspace-level OAuth apps using
  Actor Authorization based on number of paid users" — so the shared team token's
  limit scales with the team's paid Linear seats (mitigates one-token-many-agents
  contention). The naapp handles backpressure via the X-RateLimit headers and
  should fair-share across members.

## 5. Verb surface (`aw linear`) — MVP

Mirror the useful Linear MCP tools as aw verbs (team-cert auth; mutation flags):
- Reads (`library:read`-style team-cert, mutation=false): `linear-list-issues`,
  `linear-get-issue`, `linear-list-projects`, `linear-get-project`, `linear-list-teams`,
  `linear-list-users`, `linear-list-comments`, `linear-list-labels`, `linear-search`.
- Writes (team-cert, mutation=true, gated by entitlements): `linear-create-issue`,
  `linear-update-issue` (assign/status/etc.), `linear-create-comment`.
- Each write stamps `createAsUser=<member display name>` (cosmetic Linear label) and
  records the member DID (aweb audit).

## 6. New work (honest scope)

| Item | Lane | Status |
|---|---|---|
| Register the global Linear OAuth app + the per-team actor=app install flow | product/coordinator | new |
| Linear connector adapter: store + refresh a team's Linear OAuth token in the connector grant | ac/aweb-cloud (aw-coordinator) | new (table designed, adapter unbuilt) |
| Flip the composition gateway from shadow → live | ac/aweb-cloud | called-out stub swap |
| Propagate the caller's member DID through the gateway → downstream call + usage/audit record | ac/aweb-cloud | new |
| Linear naapp service + manifest (`aw linear` verbs, GraphQL brokering, createAsUser, refresh, rate-limit backpressure) | naapp build (a dev) | new |
| Webhooks → aweb events (subscribe per team, emit wake events) | naapp build | new (Phase 2) |
| Entitlements/budgets for Linear mutations | ac/aweb-cloud + naapp | new (Phase 2) |
| Per-member OAuth (actor=user) mode | naapp + cloud | new (Phase 3, optional) |

## 7. Phasing

- **Phase 0 — prove it end-to-end (manual).** Register the Linear OAuth app; one
  team installs (actor=app); a minimal naapp brokers `create-issue` with
  `createAsUser` and records the member DID. Proves actor=app + createAsUser + the
  aweb-DID record. Confirms the webhook/admin-scope nuance (see Risks).
- **Phase 1 — MVP.** Connector adapter (store/refresh token) + flip the gateway live
  + the core read/write verbs + per-member DID audit. actor=app default.
- **Phase 2 — events + governance.** Linear webhooks → aweb wake-events; entitlements
  + mutation budgets; full verb surface.
- **Phase 3 — optional.** Per-member OAuth (real Linear attribution).

## 8. Open decisions (Juan)

1. **Attribution default = actor=app + aweb-DID** (bot in Linear, cosmetic per-member
   label, real signed accountability on our side). Confirm. Per-member OAuth as a
   Phase-3 opt-in?
2. **Who owns the Linear OAuth app** — it's aweb's first-party Linear app (we
   register + maintain it); each customer team installs it. Confirm aweb owns it.
3. **Verb surface** — the MVP set above, or trim/extend?
4. **Events in scope** (Phase 2) — wake agents on Linear changes? (High value, but
   the webhook/admin-scope nuance needs a hands-on check.)
5. **Entitlements** — team-level Linear mutation policy/budgets in scope?

## 9. Risks / unknowns

- The aweb gateway + connector are **shadow/unbuilt** for external tokens — the MVP
  depends on the cloud-side lift (flip gateway live, build the Linear connector
  adapter, propagate the member DID). This is the critical path and it's
  aw-coordinator's lane.
- **Webhook creation under actor=app:** webhook creation needs `admin` scope, which
  actor=app cannot hold. So broad team-wide data webhooks need a workspace-admin to
  create them (UI / admin token) pointing at the naapp, OR we use the app's
  "Agent session events" webhook config. Exact coverage needs a hands-on check
  (Phase 0).
- **Cosmetic-label limitation:** teams must understand that in actor=app, Linear
  shows the app bot (+ name label), not the real user — unless they opt into
  per-member OAuth (Phase 3).
- **Token refresh:** 24h access token + refresh; the naapp must refresh reliably or
  the team's Linear connection breaks.
- **Wrapper maintenance:** Linear's API/MCP evolves; the naapp's verb surface needs
  upkeep to keep parity.

## 10. Ownership

I (coordinator) own the scope/design + the naapp manifest/verb design. The
cloud-side (connector adapter, gateway-live, member-DID propagation, entitlements)
is **ac/aweb-cloud — aw-coordinator's lane**; this scope goes to them for
feasibility validation (the established "I design, aw-coordinator validates
correctness" pattern). The naapp service build is a dev task (the aweb-naapp toolkit;
developer-frontend knows the naapp pattern). Product/registration decisions are Juan's.
