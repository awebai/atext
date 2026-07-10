# aweb.operations blueprint, the local/global agent line, and the aw-skill sync model

Date: 2026-06-22
Decisions: Juan, with aw-coordinator (aw/identity code-truth) + the reviewer.

## aweb.operations — the management spine

New blueprint (`~/prj/awebai/blueprints/operations/`, v0.1.0): the two roles that
**plan and staff** a team, not a self-contained vertical. Workers come from the
catalog (engineering's developer, marketing's proofreader); this pair runs them.

- **coordinator** — planning/routing brain (generalized from engineering's): turn
  goals into scoped tasks, route, review-gate, escalate. Skills: `coordinate` +
  the scoped `aweb-agent-instantiation`.
- **agent-resources (AR)** — staffing + **identity** owner. Provisions, onboards,
  runs, retires agents; owns the identity/team topology. Skills:
  `aweb-agent-instantiation` (synced) + `manage-team-identities` (AR-only).

## The local/global agent line (Juan, very clear)

The defining technical difference, and the governance split:

- **Local** agent = **no AWID identity** (no `did:aw`, no registry record),
  alias-only, ephemeral, team+machine-scoped. **The coordinator creates these
  itself, freely** (`aw team add`, default `--local`).
- **Global** agent = a durable `did:aw` AWID identity, registered, cross-team.
  **Only AR creates these** (via `manage-team-identities` / `aw id team
  add-member --global`).

Enforcement is **instructional, not hard**: `aw team add` has a `--global` flag,
and any agent with a bash tool can run any `aw` verb — skills guide, they don't
hard-gate. The skill scoping reinforces it (coordinator lacks
`manage-team-identities`). A hard-enforcement option (drop `--global` from
`aw team add`, or a capability gate) is a **pending Juan decision** (the publish
holds on his `--global` enforcement call).

## The aw-skill sync model (scoping aw mechanics to roles)

`aweb-agent-instantiation` is **aw mechanics** (materialize/run/onboard an agent)
that change as aw evolves — so its canonical lives in the **aw repo**
(`skills/aweb-agent-instantiation/`), owned by aw-coordinator. It must NOT be
universal (not every agent should staff), so it is **not** in the universal
aweb-skills plugin. Instead a **build-time sync** (`operations/scripts/sync-aw-skills.sh`,
`git show origin/main:...`) copies the canonical into ONLY the coordinator + AR
profiles. Single source of truth (aw), scoped distribution (two roles),
re-sync + re-publish when aw changes. aw-coordinator verified byte-identical.

This is the pattern for any aw-mechanics skill a blueprint needs:
canonical-in-aw + scoped build-time sync, not universal-plugin.

## Authorship/validation split (Juan)

"You own the skills and the profiles, you only need aw-coordinator to validate
correctness." I author; aw-coordinator fact-checks aw/identity claims against the
**code** (docs drift — ground in `cli/go/cmd/aw/*`, `awid-sot.md`, and the
restructuring SOTs `team-create-and-membership-model.md` +
`team-cert-issuer-seam.md` §1). The `manage-team-identities` skill was written
from a research sweep, then line-by-line code-fact-checked by aw-coordinator.

## Status at writing

Operations: reviewer-ACK'd, both skills code-grounded, instantiation synced
byte-identical — **fully publish-ready, holding only on Juan's `--global`
enforcement call**, then publish v0.1.0 + aw-coordinator runs the
materialize-prove (the full circle: an operations agent stood up by the very
instantiation skill it ships). See also
`decisions/2026-06-21-asset-scoped-profile-evolution.md` (the other live thread).
