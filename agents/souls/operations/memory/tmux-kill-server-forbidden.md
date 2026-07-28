---
name: tmux-kill-server-forbidden
description: "NEVER tmux kill-server/kill-session on the default socket — it nukes every live agent session repo-wide; isolate any tmux dogfooding on a fresh TMUX_TMPDIR socket"
metadata:
  node_type: memory
  type: project
---

Team rule after a repo-wide outage (2026-07-03): a dogfood script in another workstream ran `tmux kill-server` in an EXIT-trap cleanup. `kill-server` is a **socket-wide nuke**, and with `TMUX_TMPDIR` unset it hits the **default socket** — which hosts every live agent session across all teams in this repo, including this instance. One unguarded `kill-server` anywhere kills everyone.

Rules, effective now:
1. **NEVER** run `tmux kill-server` or `tmux kill-session` against the default socket. The harness now denies these for all instances in this repo — do not try to work around the denial.
2. Any dogfooding/testing that launches tmux (`aw team up`, `aw team add --start`, or plain `tmux`) MUST first `export TMUX_TMPDIR=$(mktemp -d)` for a fresh isolated socket, kill only **named throwaway sessions** on that proven-isolated socket, and verify nothing leaked to the default server.
3. Window/pane-level tmux commands for legitimate ops (retiring my own scratch windows) remain fine — the ban is only on server/session-wide kills of the shared socket.

Source: coordinator mail 1313703d (verified), 2026-07-03.
