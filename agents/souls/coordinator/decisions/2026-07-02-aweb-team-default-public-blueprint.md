# aweb.team: one default public blueprint; materialize split from shelf

Date: 2026-07-02
Owner: coordinator (with aw-coordinator; Juan decided)

## What Juan decided

- The two public blueprints (`aweb.development` 0.1.0, `aweb.support` 0.1.1)
  are **combined into one**: **`aweb.team`**, the **default public blueprint**
  — the seed catalog `aw` points at out of the box.
- Library is understood from first principles as **two separable things**:
  1. **Public blueprints** — unauthenticated references/seeds to start from
     (reads on library.aweb.ai already need no auth; verified with plain GET).
  2. **Shelf machinery** — the authed, team-private evolution loop
     (import-to-shelf, propose/approve, minted versions).
- **Agent materialization separates from the shelf**: `aw` materializes
  directly from a library URL arg (→ env var → our library) and a blueprint
  arg (→ env → `aweb.team`). The shelf/library machinery becomes a plugin a
  team **knowingly adds** when it wants the evolution loop.

## Why (the evidence that decided it)

- Adoption is per-profile (`POST /v1/shelf/import` keyed by team+blueprint+
  profile); the blueprint boundary gates nothing — the dev/support split cost
  users pairing friction and bought nothing.
- Both old descriptions said "pair it with the other one"; support's content
  hard-coded `aweb.development/developer` refs; the coordinator (router) was
  split from the developers (routed).
- With the blueprint arg defaulting away, the user-facing unit is the
  **profile** (`aw team add ada@developer`); the blueprint is a curated index
  + recommended composition. One first-party seed catalog follows.

## Design points agreed in the discussion

- **One contract spec** (import-payload.v1 + materialization semantics) that
  BOTH aw and library implement, with cross-tests — we already hit
  canonical/digest drift in the ops pilot.
- **Lockfile refresh model**: public-seed homes pin resolved source URL +
  content digest in the materialize pin (ref.json) and update only on explicit
  refresh; shelf homes update through the reviewed mint.
- **Upgrade seam**: a plugin-free team that later adds the shelf backfills by
  adopting running agents' profiles from their pins — design it, don't
  discover it.
- **Supply-chain note**: the env-redirectable source means materialize must
  always record and print resolved URL + digest.

## Work this implies

- Author `aweb.team` in `~/prj/awebai/blueprints` (all 8 profiles; defaults =
  coordinator 1, agent-resources 1, developer 2, reviewer 1, rest 0). Same
  pass fixes: published `NOTES-ours.md` leak (deployer + reliability — the
  file itself says it must not be public), stale README (`engineering/`,
  `missions.yaml`), empty tags, cross-refs → `aweb.team/...`, drop the
  "pair with" prose.
- Publish `aweb.team`, then `DELETE /v1/blueprints/aweb.development` and
  `aweb.support` (endpoint exists).
- aw-side: materialize-from-URL + defaults chain + pin recording (aw team /
  aw-coordinator's side, division to be confirmed).

## Alignment outcome (2026-07-02, same day)

- aw-coordinator ACK'd the division: they own the contract spec + aw-side
  materialize-from-URL + pin recording; we own the aweb.team seed content.
  Epic **default-aaeq**; our deliverable is **default-aaeq.7**.
- Three contract locks agreed: (1) the public catalog response is
  self-sufficient for materialize + pin (files with sha256, blueprint and
  profile ref/version/digest — no shelf round-trip); (2) the materializer
  verifies files against the profile digest, so integrity survives without
  import-to-shelf; (3) cross-tests are shared conformance vectors both aw
  and library run. aaeq.1 (the spec) is the interlock — we sign off on the
  draft before they build.
- **HOLD**: publish of aweb.team gated on (a) the aw-side default-switch
  landing and (b) v1.26.22 launch stability — shipped onboarding still
  points at the old blueprints. aw-coordinator ACKs publish.
- **Deletion gate is WIDER (added 2026-07-02)**: the AC Team Builder wizard
  (ac-frontend) is a live consumer of GET /v1/blueprints. Deletion of
  aweb.development/aweb.support waits for aw-coordinator's ACK **and** the
  relayed ac-frontend wizard-cutover signal. Sequence: I publish →
  aw-coordinator signals ac-frontend → wizard cuts over to aweb.team →
  signal relayed → I delete. Transition window shows three overlapping
  blueprints in the wizard — keep it short.
- **Simplified (later same day)**: ac-frontend made the wizard data-driven
  (exactly one blueprint in the catalog → skip the chooser and seed from its
  default_counts; more → chooser renders; stale persisted plans cleared).
  Ships before publish with zero risk, auto-cuts-over on publish.
- **PUBLISHED (2026-07-02, Juan's direct instruction)**: aweb.team 0.1.0 is
  live on library.aweb.ai — 200, server digest = local `aw blueprint
  inspect` digest (sha256:8b87a0b0…), publish via `aw id request POST
  /v1/blueprints/import --team-auth` from the aweb.ai team home. Juan also
  simplified the wizard: HARDCODE default to aweb.team; user selection only
  when more blueprints exist. Deletions of the old two still held on the
  wizard-live signal. Tags: the import route ignores them, but
  `PUT /v1/blueprints/{ref}/tags` (owner-team-scoped) works — aweb.team is
  tagged `starter, team` live (set 2026-07-02 from the aweb.ai team home).
- **Catalog ownership is MIXED — matters for the deletion**: the old
  blueprints were published with the default:atext.aweb.ai team cert (ada,
  per task aacd); aweb.team is owned by the aweb.ai team (my publish from
  the hestia home). DELETE is owner-team-scoped, so deleting
  aweb.development/aweb.support must be signed by the **atext team cert**
  (via ada or a home carrying it), not the aweb.ai one.
- **Superseded gates (kept for history)**: the funnel has NO
  live traffic yet, so all transition-window sequencing concerns are moot —
  publish and delete plainly when gates pass, no atomicity needed. Gates:
  publish on aw-coordinator's two-gate ACK (aaeq.3 landed + v1.26.22
  stable); deletion additionally needs the data-driven wizard verified live
  (so no old-shaped consumer reads a deleted catalog). Publish-before-delete
  still the natural order. No batch endpoint exists (verified the route
  table); none warranted.
- Authored, validated (inspect + local materialize green for all 8
  profiles), and pushed: branch `aweb-team` in the blueprints repo, commit
  b4f1974. NOTES-ours content parked in `shelf-notes/` at the repo root for
  the aweb team to adopt onto their shelf. Tags are a publish-time request
  field (not blueprint.yaml); decided at publish: **team, starter** —
  aw-coordinator rightly flagged that "engineering" would mis-shelve a
  default that now carries the support/ops roles; nothing domain-scoped
  until the catalog has domains to filter. shelf-notes/ gets deleted from
  the repo once aw-coordinator signals the notes are adopted onto their
  private shelf (existing shelf machinery, no aaeq.5 dependency).

- **aaeq.1 signed off (2026-07-02)**: the contract is
  `docs/blueprint-materialization-contract.md` in the aweb repo (commit
  1b032d31). Confirmed: no blueprint digest on the public response in v1
  (profile digest is the anchor; blueprint digest would false-drift
  single-profile homes), U+2028/U+2029 prohibition (verified zero in
  aweb.team). The library service is OUR code — symlink rejection filed as
  **default-aaeq.8** (digest.py collect_files follows symlinks today),
  assigned to developer.

- **aw default-switch LANDED (2026-07-02)**: aaeq.3 (materialize-from-URL,
  --library-url/AWEB_LIBRARY_URL/default + --blueprint/AWEB_BLUEPRINT/
  aweb.team) + aaeq.4 (pinned refresh, fail-closed integrity, managed-set
  pruning) merged to aw main 86102bf4, reviewed, validated against prod
  library incl. the aweb.team default path. Not yet in a released aw — not
  a blocker (nothing released references the old blueprints). Deletion gate
  is now solely: hardcoded-aweb.team wizard live (relayed signal).

- **CUTOVER COMPLETE (2026-07-03)**: after the AC-clean signal (aweb.ai site
  + wizard v0.7.0 live on aweb.team) and Juan's go, ada deleted both old
  blueprints with the atext team cert (200 each; GETs now 404). Public
  catalog verified: exactly `[aweb.team]`, tags starter/team. Full arc done:
  publish → contract (aaeq.1/2/8) → aw 1.30 default → naapp sites → AC
  site/wizard → deletion. Follow-on tracked: default-aafd (homes pinned to
  the deleted blueprints fail explicit refresh; migrate via re-pin or
  adopt-from-pin when aaeq.5 lands).

## Open
- Where marketing roles land: earlier direction was a sibling
  `aweb.marketing` blueprint ([[upcoming-marketing-blueprint]]), but the
  proofreader already drifted into the dev blueprint and `aweb.team` as THE
  default suggests marketing roles become profiles in it. Not decided —
  ask Juan when marketing work starts.
