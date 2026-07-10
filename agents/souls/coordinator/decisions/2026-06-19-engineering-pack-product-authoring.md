# Engineering pack: product authoring, home, and showcase pairing

Date: 2026-06-19
Owner: coordinator (I own the product-quality engineering pack)

## What

Authored the first-party **Engineering AI Team Starter Pack**
(`aweb.engineering-pack`) as a real product pack, superseding the thin
`.2.9` fixture. Three profiles — coordinator, developer (1–4), reviewer —
each with rich `instructions.md`, skills, and a status/handoff/review
template, in the fixture pack format, targeting the `aw` CLI.

## Sources synthesized

- beadhub `defaults/roles/{coordinator,implementer,reviewer}.md` — proven
  production roles (primary).
- `~/.claude/agents/{code-reviewer,root-cause-debugger}.md` — the review
  rubric (blocking vs non-blocking) and the root-cause debugging method.
- Our own atext souls (developer/reviewer) — the aw-based team patterns.
- Juan's `~/.claude/CLAUDE.md` — the engineering bar (TDD, smallest correct
  change, no mocks in e2e, root-cause, honest pushback, naming/comment rules,
  scope discipline). Adapted bdh commands to `aw`.

## Decisions (Juan, 2026-06-19)

- **Home:** a dedicated first-party packs repo, NOT atext. Lives at
  `~/prj/awebai/packs` (git, branch `main`); the pack is `packs/engineering/`.
  See [[engineering-pack-home]].
- **Publish:** hold until Juan reviews the profile *content*; then publish
  `v0.2.0` to live Library, superseding the `v0.1.0` fixture pack
  (live digest `sha256:30159b1e...`).
- **Showcase runtimes** (for the `library.aweb.ai` two-profile demo):
  **coordinator on claude-code + channel, reviewer on pi + extension.**
  No profile change needed — the reviewer profile already lists `pi` among
  its `runtime_hints`, so the aw roster puts the reviewer instance on pi.

## Open / held

- **Harness-selection field:** aw-developer's B leaf derives `runtime_kind`
  for harness selection. aw needs a STRUCTURED field, not prose. aw-coordinator
  is pinning the exact field + allowed values with aw-developer (likely
  `runtime_hints` = `claude-code|codex|pi`). **Do not finalize the showcase
  profiles' runtime field until they confirm it.** Then set it on both
  showcase profiles to match what the B leaf parses.
