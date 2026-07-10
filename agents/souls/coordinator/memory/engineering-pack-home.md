# Engineering pack lives in its own repo

The first-party engineering pack source is NOT in atext. It lives in a
dedicated blueprints repo (renamed from `packs` in the 2026-06-21 pack→blueprint
rename — see `decisions/2026-06-21-pack-to-blueprint-rename.md`):

- Repo: `~/prj/awebai/blueprints` (git, branch `main`).
- Blueprint: `blueprints/engineering/` — `aweb.engineering`, profiles
  coordinator / developer / reviewer.

I own this pack. **v0.2.2 is the live latest** on library.aweb.ai (2026-06-20),
triple-verified materializing. v0.2.0 broke aw materialize via a folded block
scalar `mission: >` trailing newline (NOT the em-dash — see
[[aw-materializer-multibyte-utf8-bug]]); v0.2.1 (ASCII) did not fix it; v0.2.2
uses folded-strip `>-`. Pack digest `sha256:100eb588...`; profiles coordinator
`dd94e17f`, developer `5ae4c89b`, reviewer `21fc56b5`. Older rows retained
(collision guard). Use `>-` or plain scalars in blueprint content until aw .3.24
lands.

**Update 2026-06-21 — catalog now has TWO blueprints:** `aweb.engineering`
v0.2.3 (digest `67fc4364`, tags development/engineering/software) and
`aweb.marketing` v0.1.0 (proofreader profile, tags content/copywriting/marketing).
All blueprint skills now carry valid SKILL.md frontmatter — see
`docs/skill-authoring-spec.md` (the authoritative format + checklist). `expected_apps`
is trimmed to `[library, tasks]` only — **never list an app we do not have**
(audit/secrets/github were phantoms Juan cut).

**GOTCHA: tags are mutable API-set metadata, NOT in the source or the digest, so
a RE-PUBLISH WIPES them.** Re-apply `set-blueprint-tags` (via `aw id request
--team-auth PUT /v1/blueprints/<ref>/tags`) after every publish/reseed.

Runtime selection (changed 2026-06-21, aw `aa7b45e0`): the runtime is the
operator's **explicit CLI choice** — `aw team add
NAME@aweb.engineering/coordinator --runtime claude-code` (omitted → claude-code,
a CLI default, NOT read from the profile); roster form
`--profile coordinator=claude-code`. `runtime_hints` + `runtime_assumptions`
are now **advisory, queryable** metadata the operator reads (`aw blueprint
inspect` / `library get-profile`), never auto-applied. get-profile already
exposes them, so the old "expose runtime_hints" work is done.

See decision: `decisions/2026-06-19-engineering-pack-product-authoring.md`.
