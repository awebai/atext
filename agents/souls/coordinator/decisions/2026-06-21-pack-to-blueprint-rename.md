# Rename: "profile pack" / "pack" → "blueprint" (full, cross-lane)

Date: 2026-06-21
Decision: Juan — rename the concept everywhere to **blueprint**, the full
contract (not just copy), across all three lanes (library + aw + AC), **now**
while there is no real customer adoption. Post-launch this becomes a breaking
change with compat shims; pre-customer it is a clean cutover.

**STATUS: LIBRARY RENAME GO (Juan, 2026-06-21).** Full rename, NO backwards
compatibility, NO tech debt; DROP + reseed the DB (nobody uses library yet).
developer-2 leads. DO NOT tell aw-coordinator or ac-coordinator until the new
contract is LIVE — then notify them with the new contract; aw/AC adopt after.
Sub-decisions RESOLVED: API `/v1/blueprints`; published id `aweb.engineering`
(drop the type suffix); publish op `/v1/blueprints/import`; rewrite the single
001 migration with the blueprint schema (no rename migration).

A blueprint is a published, versioned, named definition of a team of agent role
profiles, that a team adopts onto its shelf, customizes, and runs.

## Canonical mapping (single source of truth — all lanes follow this)

| Old | New |
|-----|-----|
| profile pack / pack | blueprint |
| `/v1/profile-packs` | `/v1/blueprints` |
| `/v1/profile-packs/{pack_ref}` | `/v1/blueprints/{blueprint_ref}` |
| `/v1/profile-packs/{pack_ref}/profiles/{profile_ref}` | `/v1/blueprints/{blueprint_ref}/profiles/{profile_ref}` |
| `/v1/profile-packs/import` (publish) | `/v1/blueprints/import` |
| `pack_ref`, `pack_version` | `blueprint_ref`, `blueprint_version` |
| `source_profile_pack_ref` / `_version` | `source_blueprint_ref` / `_version` |
| manifest tool `list-packs` | `list-blueprints` |
| manifest tool `get-pack` | `get-blueprint` |
| aw verb `aw library list-packs` / `get-pack` | `list-blueprints` / `get-blueprint` |
| DB `profile_packs`, `pack_profiles` | `blueprints`, `blueprint_profiles` |
| canonical schema "import-payload.v1, pack-relative" | "blueprint-relative" (same bytes form, renamed semantics) |
| published id `aweb.engineering-pack` | `aweb.engineering` (drop the redundant type suffix; PROPOSED) |
| source repo `prj/awebai/packs`, `pack.yaml` | `prj/awebai/blueprints`, `blueprint.yaml` |
| docs copy "pack" / "profile-pack catalog" | "blueprint" / "blueprint catalog" |

Open sub-decisions (team + Juan refine, not blocking the plan): exact published
id form (`aweb.engineering` vs `aweb.engineering-blueprint`); whether the
publish op is named `publish-blueprint` vs keeping `import`. Shelf/binding/
materialize ops keep their names; only their `*_pack_ref` fields rename.

## Sequencing (the shared manifest contract must flip cleanly)

The manifest is the shared contract: library serves the tool names, aw parses
them, AC consumes them. They must flip together or dispatch breaks. Anchor the
cutover on the **aw release** aw-coordinator is already cutting:
1. All three lanes prepare on branches against this spec.
2. aw's release handles the blueprint verbs + manifest tool names.
3. library deploys the new API + manifest + the re-published blueprint.
4. AC onboarding uses blueprint terms.
Converge the exact deploy order with aw-coordinator (owns release timing).

## DB + catalog (pre-customer, so clean)

Clean rename migration (we control all the data). Re-publish the engineering
blueprint under the new schema/id; DROP the stray `atext.aw-developer-live-smoke`
test pack so the public catalog ships clean.

## Lanes + owners

- **library** (coordinator's team): API paths, fields, DB tables/migration,
  docs (llms.txt/reference/landing), library's ReferenceCopy strings, the
  re-published blueprint, the source repo. The aweb-naapp toolkit stays generic
  (library supplies the renamed copy) — verify no "pack" leaked into toolkit
  defaults.
- **aw** (aw-coordinator): verbs, manifest tool-name parsing, conformance,
  release anchoring.
- **AC** (ac-coordinator): onboarding/funnel copy + pack references.
