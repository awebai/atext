---
name: instances-process-queued-mail-despite-no-heartbeat
description: An agent absent from the roster (no heartbeat) or unresponsive to a chat-wake can still be processing queued mail and acting — don't declare it "offline/stuck."
metadata:
  type: feedback
---

`aw workspace status` only lists agents with a recent heartbeat, and a
`chat send-and-wait` can return "not connected / no reply" (even after a read
receipt) — but NEITHER means the agent is dead. Observed 2026-06-17: I called
operations "offline" then "stuck" when it was missing from the roster and didn't
answer two chat wakes. It was working its MAIL queue the whole time — it
processed my queued `aw mail` deploy directive, deployed folio to prod, and
replied via mail.

**Why:** Juan pushed back ("why offline? just chat to wake them"). The deeper
truth: a queued mail directive to an instance gets processed when its session
next ticks/reconnects, independent of roster heartbeat or chat responsiveness.
Roster heartbeat and chat-wake latency are poor proxies for "will it act."

**How to apply:** For a handoff/deploy directive, send `aw mail` and wait for
the mail reply — do not conclude "offline" from an empty roster or a silent
chat. Latency can be long, so for TIME-CRITICAL work still escalate to Juan
(launch the session) AND keep the mail queued — but don't report an agent as
dead/stuck based on heartbeat alone. `aw whoami` checks YOUR identity
([[log-awid-registry-503s]]); there's no equivalent cheap probe for a teammate's
liveness, so trust the mail-reply path. See [[verify-main-worktree-before-merge]].
