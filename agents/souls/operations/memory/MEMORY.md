# Memory

One fact per file, indexed here. See the `self-maintenance` skill.

- [log-awid-registry-503s](log-awid-registry-503s.md) — Juan's directive: log every "AWID registry unavailable" 503 to `docs/awid-registry-incidents.md` (ts, cwd, command, retry, impact); ops keeps its own log
- [render-env-single-key-endpoint](render-env-single-key-endpoint.md) — Render bulk PUT env-vars REPLACES ALL; use the single-key endpoint to change one or you wipe the rest (outage)
- [tmux-kill-server-forbidden](tmux-kill-server-forbidden.md) — NEVER tmux kill-server/kill-session on the default socket (nukes every agent session repo-wide); isolate any tmux dogfooding on a fresh TMUX_TMPDIR socket
