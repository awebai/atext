# folio migrations: single clean 001 until first deploy, forward-only after

Date: 2026-06-15
Status: adopted (Juan's call, via operations)

## Decision

While folio has **no deployed database** (greenfield), all schema lives in a
single `001_initial.sql`. Pre-deploy schema changes are folded directly into
`001` — no forward migrations. After folio's **first production deploy**,
`001` is frozen forever and every schema change is a forward migration
(`002`, `003`, …).

## Why

A brand-new system should not start its `schema_migrations` history with
tech debt (e.g. `002` that only patches columns `001` could have declared).
atext launched from one clean migration. folio's Render service + fresh Neon
were staged by operations but never deployed, so there is no immutable
history to protect yet.

## How this reconciles the M8 episode

During M8, reviewer-2 (correctly, under the immutability invariant) required
a forward `002_editable_present_links.sql` rather than editing the already
existing `001`. That was the right *safe-under-uncertainty* call: a forward
migration is mandatory IF a DB has applied `001`. Once Juan confirmed
greenfield, we squashed `001`+`002` back into a single `001` for the first
deploy. **Both are correct at their moment** — the deciding fact is whether
any DB has applied the migration yet.

## Operational consequence

The commit handed to operations for the first deploy must contain exactly
one migration file (`001_initial.sql`). The reviewer's immutability invariant
re-engages the instant that deploy applies it. See the reviewer soul's
`patterns/` and [[verify-main-worktree-before-merge]].
