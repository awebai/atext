# Asset-scoped profile evolution

Date: 2026-06-21
Decision: Juan — the profile-evolution loop is **asset-scoped**: agents propose,
and reviewers bless, **individual assets** within a profile (the instructions, a
skill, an artifact — and they can CREATE new ones), not whole profiles. **No
backward compatibility** — change the library proposal/mint model cleanly (no
real users yet); do not preserve the whole-profile proposal contract for compat.

## The loop

1. **Evolve** — an agent edits an asset in place under `.aw/profile/`
   (`instructions.md`, `skills/<name>/SKILL.md`, `artifacts/<f>.md`), or adds a
   new one.
2. **Propose** — `aw library propose --asset <path> [--asset <path> …] [--delete <path>] --summary … --rationale …`.
   aw reads `.aw/profile/`, builds a CHANGESET (one or more assets: modify /
   create / delete), records each asset's **base digest** (from the profile's
   part-baselines / `ref.json`), and POSTs it.
3. **Bless** — a reviewer sees a small per-asset diff and approves. Any team
   member (the proposer or a teammate) can; auth is team-cert.
4. **Mint** — blessing applies the changeset to the **current** shelf profile
   (swap/add/remove the asset(s)), carrying forward every unchanged asset +
   provenance + baselines, and mints a **new profile version**. The profile
   stays the versioned, materialized unit; proposals/blessing are by asset
   within it.
5. **Upgrade** — `aw library update`: other agents pull the new profile version
   into their home (preserving any un-proposed local edits via the existing
   3-way merge, or re-materialize if clean).

## Model details

- **Asset = a part.** Files (`instructions.md`, skill files, artifacts) and
  `profile.yaml` fields (mission, accepted_work, …). The `part_baselines` column
  already enumerates these per-asset digests.
- **Conflict = per-asset reject-stale.** If a proposed asset's base digest no
  longer matches the current shelf profile's asset digest, reject (re-propose on
  latest). Non-overlapping asset proposals never conflict.
- **Create-new-skill is a changeset.** materialize installs skills from the
  `profile.yaml` `skills:` list, so a new skill = `{new skills/<n>/SKILL.md +
  the profile.yaml skills[] entry}` proposed atomically. Hence `--asset` is
  repeatable.
- **Bless granularity.** A proposal is one changeset (usually one asset);
  blessing it mints one new version. (Future: independent per-asset proposals
  that compose — out of scope for v1.)

## Lanes

- **Library (coordinator's team):** replace the whole-profile proposal/mint with
  the asset-scoped model — proposal carries a changeset of assets + per-asset
  base digests; mint applies the changeset to the current profile; per-asset
  reject-stale. The `part_baselines` + the existing reject-stale guard are the
  starting point.
- **aw (aw-coordinator):** `aw library propose --asset <path>…` (package the
  changeset from `.aw/profile/`) and `aw library update` (pull a blessed version
  into the home; 3-way-merge local un-proposed edits).
- **Proof:** one e2e that is Juan's scenario — proofreader adopted → agent A
  improves `skills/proofread/SKILL.md` → propose that asset → bless → other
  proofreaders `aw library update` and run the improved skill; plus a
  create-new-skill changeset that appears after blessing.
