# Memory

One fact per file, indexed here. See the `self-maintenance` skill.

- [aweb-css-generic-class-collisions](aweb-css-generic-class-collisions.md) — aweb.css owns short generic classes (.roster/.tag/.card…); prefix app-local naapp page classes (browse-…) or they silently inherit design-system rules.
- [naapp-page-preview-without-db](naapp-page-preview-without-db.md) — preview a naapp page design faithfully with real chrome+CSS by rendering via naapp.page() and inlining aweb_css()+fonts; serve over http (Playwright blocks file://).
- [push-branch-before-handoff](push-branch-before-handoff.md) — push your handoff branch (git push -u origin <branch>) and verify with git ls-remote before telling the coordinator it is ready to merge; a local-only commit is not a handoff.
- [tmux-dogfooding-isolation](tmux-dogfooding-isolation.md) — never kill the default tmux server/session; isolate any tmux dogfooding with fresh TMUX_TMPDIR, named throwaway sessions, and leak checks.
