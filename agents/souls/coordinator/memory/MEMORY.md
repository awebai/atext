# Memory

One fact per file, indexed here. See the `self-maintenance` skill.

- [Instance worktrees need explicit push](instance-worktrees-need-explicit-push.md) — verify `git ls-remote` before routing review; pgdbm symlink path.
- [Post-reboot ssh-agent is empty](post-reboot-ssh-agent-empty.md) — `ssh-add --apple-load-keychain` to fix publickey-denied pushes; folio ≠ atext repo.
- [Verify main worktree before merge](verify-main-worktree-before-merge.md) — HEAD can drift onto a review branch; merge silently no-ops. Check `git branch --show-current` first.
- [aweb mail WAF blocks security jargon](aweb-mail-waf-blocks-security-jargon.md) — reword neutrally or `aw mail send` 403s; durable fix is a scoped Cloudflare exception.
- [Browser features: verify against a running instance](browser-features-verify-against-running-instance.md) — require Playwright-against-running-folio; TestClient/static-server "verified" misses JS breakage.
- [Log every AWID registry 503](log-awid-registry-503s.md) — Juan's directive: record timestamp + cwd + exact action + recovery in `docs/awid-registry-incidents.md`. Also: run `aw` only from home (non-home cwd → wrong `grace` identity).
- [Instances process queued mail despite no heartbeat](instances-process-queued-mail-despite-no-heartbeat.md) — don't call an agent "offline/stuck" from an empty roster or silent chat; queued mail still gets processed and acted on.
- [Engineering pack lives in its own repo](engineering-pack-home.md) — pack source is `~/prj/awebai/packs` (not atext); I own it; v0.2.1 (ASCII) live on Library.
- [aw materializer rejects folded scalars](aw-materializer-multibyte-utf8-bug.md) — use `>-` or plain scalars in profile.yaml (not bare `>`); the trailing newline trips aw's validator, not multibyte UTF-8.
- [upcoming-marketing-blueprint](upcoming-marketing-blueprint.md) — Juan's next: a marketing blueprint (`aweb.marketing`, confirmed a blueprint not an app), first profile a proofreader that reviews copy/web pages.
- [ai.aweb workspace-key exposure incident](ai-aweb-repo-key-exposure-incident.md) — signing keys were safe (symlinks into private co.aweb); workspace.yaml api_keys were the real exposure; repo flipped private 2026-07-10, rotation pending.
