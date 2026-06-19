# folio `aw folio` verbs ship via a manifest, not a hand-written binary

Date: 2026-06-16
Status: adopted (aweb team's call; folio confirmed). Supersedes the
external-binary brief.

## Decision

`aw folio <verb>` is delivered by a **manifest-driven generic dispatcher**
owned by the aweb cli team, not by a folio-shipped binary. folio publishes
**one static manifest** conformant to the frozen schema
(`aweb/docs/restructuring/app-manifest-schema.md`, commit `d0551de6`,
"frozen v1"). The same manifest drives three consumers identically: the
hosted gateway's MCP tools, the `aw folio` CLI verbs (a generic dispatcher
over `aw id request --team-auth`), and the aweb.ai hub listing.

## Why this beats my external-binary brief

My `aw-plugin-brief.md` recommended the kubectl/gh model: `aw <name>` execs an
`aw-<name>` binary. Its whole reason to exist was that folio is a **private
repo** and a Python console script was undistributable — so I proposed shipping
a binary release artifact. The manifest approach dissolves that problem
outright: a private repo can publish a **static declaration** even when it
can't publish a usable binary. No ABI coupling, no per-language plugin, no
release-artifact pipeline. The brief is marked SUPERSEDED in
`folio/docs/aw-plugin-brief.md` (kept only as the rejected-path record).

## Folio's part (the only folio-team calls)

- **Verb names** are folio's product-facing call; everything else in the
  schema is frozen. Confirmed all 14 from the schema's worked-example table,
  grounded 1:1 against `folio/src/folio/api.py`:
  create, list, show, versions, append, append-template, present, revoke,
  theme-get, theme-set, asset-image, asset-video, asset-get, billing.
  - `show` = GET the document (read); `present` = mint the link. Do not
    re-conflate these (the old aaag.5 text did).
  - `append` (raw UTF-8 markdown, `--body-file`) and `append-template` (json
    slots) are two verbs because they are two endpoints. aaai.3's "version"
    shorthand = `append`.
  - `append` is the one **raw**-body verb; everything else is json or bodiless.
- folio ships its manifest when the cli team's dispatcher
  (`default-aaai.2`) + conformance vectors (`default-aaai.4`) land. Build is
  tracked in `default-aaai.3` (the e2e proof: create/append/show/present/
  theme-set + image upload against a real instance, generic dispatcher path
  asserted, no mocks). The old folio task `default-aaag.5` is closed and
  annotated as superseded-in-approach.

## Open item to resolve before folio writes the manifest

The schema declares the app's `llms_txt`/`skills` paths but **not where the
manifest itself is served** from origin. folio needs that well-known path from
the cli team before publishing. Asked in the reply (conversation
`253b1a3a`). Offered a real manifest artifact early so `default-aaai.4`
conformance vectors key off real bytes, not the doc table.

See [[verify-main-worktree-before-merge]] and the greenfield-migration
decision for the folio-repo working rules.
