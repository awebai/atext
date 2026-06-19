# Library profile model v2: public packs + private shelves

Date: 2026-06-19
Status: ADOPTED — Juan, 2026-06-19. Supersedes the per-profile `visibility`
flag from chunk2. Reshapes the team-facing model; the frozen cross-lane byte
contract (digests, import-payload, import-return, materialized-home) is
UNCHANGED — no re-freeze.

## The model

Two structural sides; visibility is structural, not a flag.

- **Packs = the public catalog.** Always public. Versioned (a producer ships
  better versions). Tagged. Owned by a publishing team (a team owns zero or more
  public packs). This is the global "store" everyone browses.
- **Shelf = a team's private working copies.** Always private. A team's shelf is
  all the profiles it sees day-to-day. Shelf profiles carry tags (team's own
  org). Bindings + materialize target **shelf profiles ONLY**.

A team's everyday view is its shelf. It only sees public packs when it
explicitly lists/browses the catalog.

## Getting a new profile (two ways)

1. **Create** a new shelf profile directly (team-owned, private).
2. **Import-to-shelf**: browse public packs, copy a profile from one onto the
   shelf. Copy-on-add — an independent private copy with source provenance
   (`source_pack_ref`/`version`/`digest` + per-part baseline digests).

## Operations / surface

- `create` shelf profile (team-cert) — new private profile.
- `import-to-shelf` (team-cert) — copy a public-pack profile onto the shelf.
- direct **versioning** of an owned shelf profile (team-cert) — new content
  version (new digest), the continuous-update path.
- **publish-profile** (team-cert) — copy a shelf profile into a team-owned
  public pack (existing or new). This is "make public" — a publish-copy, NOT a
  flag flip. The published pack profile is a snapshot.
- **publish-pack** (team-cert) — a producer uploads/updates a public pack in the
  global catalog (the former `import`, repurposed to public). Pack versioning
  lives here.
- `update-from-source` (team-cert) — see below.
- bindings (`agent -> shelf profile`) + `materialize` (shelf profile -> home)
  unchanged in mechanism, now targeting shelf profiles.
- proposals lifecycle (create/list/approve/reject) + **version-minting on
  approve** (deferred earlier; mints a new shelf-profile version via the frozen
  profile-payload digest).
- catalog reads: public = packs (+ their profiles); team view = its shelf.

## REMOVED by this model

- the per-profile `visibility` flag and `set-visibility` endpoint (chunk2) —
  visibility is now structural (in-a-public-pack = public; on-a-shelf = private).
  `set-tags` stays (tags on shelf profiles AND packs).

## Per-part update-from-source (the merge)

"Update only the parts you haven't evolved." A profile's content is files, so
**parts = per-file** (`instructions.md`, each skill file, each artifact file)
plus structured fields (`mission`, `accepted_work`, `runtime_assumptions`,
`memory_policy`). Each part tracks a **baseline digest** (its content at
copy/last-sync from the source pack version) and its current content.

`update-from-source` is a per-part 3-way merge:
- baseline = part at last sync (from source pack version)
- ours = current shelf part
- theirs = the newer pack version's part
- if `ours == baseline` (un-evolved) -> take `theirs`; else keep `ours`.

So evolved parts are never clobbered; un-evolved parts pick up upstream
improvements. "Evolved" = current part digest != baseline digest. `default`
preserves evolved parts; an explicit force-take-theirs is a possible later
override.

## Sequencing (build order)

1. **Core shelf model**: structural visibility (remove the flag), shelf as
   private per-team copies, create + import-to-shelf (copy-on-add with per-part
   baseline provenance), publish-profile + publish-pack, bind/materialize on
   shelf, direct versioning, proposal version-minting. Tags on shelf + packs.
2. **update-from-source** per-part merge — its own focused build + tests (the
   most complex piece).

The proven core (import/bind/materialize mechanisms, byte-parity digests,
catalog, tags, proposals-lifecycle) is the foundation; this reorganizes it
around shelf vs pack. See [[2026-06-19-library-profile-visibility-and-continuous-improvement]]
(its per-profile-visibility flag is superseded here; the
content-digest-excludes-metadata principle still holds).
