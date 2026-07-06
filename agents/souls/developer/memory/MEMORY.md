# Memory

One fact per file, indexed here. See the `self-maintenance` skill.

- [aweb-css-generic-class-collisions](aweb-css-generic-class-collisions.md) — aweb.css owns short generic classes (.roster/.tag/.card…); prefix app-local naapp page classes (browse-…) or they silently inherit design-system rules.
- [naapp-page-preview-without-db](naapp-page-preview-without-db.md) — preview a naapp page design faithfully with real chrome+CSS by rendering via naapp.page() and inlining aweb_css()+fonts; serve over http (Playwright blocks file://).
- [push-branch-before-handoff](push-branch-before-handoff.md) — push your handoff branch (git push -u origin <branch>) and verify with git ls-remote before telling the coordinator it is ready to merge; a local-only commit is not a handoff.
- [naapp-getting-started-invariant](naapp-getting-started-invariant.md) — a naapp landing has ONE getting-started that goes zero→the naapp's core value in minimum steps; no generic onboarding + separate what-it-does split.
- [aweb-command-flows-verify-by-execution](aweb-command-flows-verify-by-execution.md) — a command JOURNEY is only correct if RUN end-to-end; schema/manifest reads prove shape not runnability; read e2e tests, get executed transcripts, describe agent-cert actions rather than panelling them.
- [tmux-dogfooding-isolation](tmux-dogfooding-isolation.md) — never kill the default tmux server/session; isolate any tmux dogfooding with fresh TMUX_TMPDIR, named throwaway sessions, and leak checks.
