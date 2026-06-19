---
name: log-awid-registry-503s
description: Juan's standing directive — log every "AWID registry unavailable" 503 with exactly what was attempted, whether retry recovered it, and what was affected.
metadata:
  type: feedback
---

When any `aw` command returns `http 503: {"detail":"AWID registry
unavailable"}`, immediately append an entry to
`docs/awid-registry-incidents.md`: precise timestamp
(`date '+%Y-%m-%d %H:%M:%S %Z'`), **the directory `aw` was run from (`pwd`)**,
the exact command/action attempted, whether a retry or fallback (e.g.
`send-and-leave` instead of `send-and-wait`) recovered it, and what (if
anything) was lost or delayed. The directory matters: running `aw` from the
wrong cwd gives a *different* error ("current directory is not initialized for
aw"), so recording cwd proves a 503 is a real registry outage, not a
wrong-directory mistake — always run `aw` from the coordinator instance home.

**Why:** Juan asked for this 2026-06-17 during the folio manifest deploy, when
the registry was intermittently 503-ing and operations was offline — he needs a
record to diagnose registry instability and to be sure no coordination action is
silently dropped by an outage.

**How to apply:** Don't just retry and move on — record it first (or right
after recovering). Retries usually succeed within seconds; `send-and-leave`
delivers when `send-and-wait`'s SSE stream 503s. Direct HTTPS to folio.aweb.ai
(prod curl / three-way sha) does NOT traverse the registry, so prod verification
stays reliable mid-outage. See [[verify-main-worktree-before-merge]] and
[[aweb-mail-waf-blocks-security-jargon]] for other aw-channel gotchas.

**HARD RULE — run `aw` ONLY from the instance home; never from a non-home
cwd.** Juan, 2026-06-17: "the problem comes when you run aw and you are not in
your home cwd." Running `aw` from the repo ROOT resolves the WRONG identity
(`grace` = `aweb:juan.aweb.ai`) instead of your alias — silently sending as the
wrong identity / `agent not found` on teammates. This is a DIFFERENT failure
from a 503 (see `docs/awid-registry-incidents.md`), and the more dangerous one
because it's silent. So: NEVER combine `cd …` and `aw …` in one shell call;
keep `git`(repo) and `aw`(home) in separate calls; when a result looks like
"flakiness," run `aw whoami` first — if it shows `grace` not your alias, it's
wrong-cwd, not the registry. Related but milder: [[folio-separate-repo]] (aw
from a folio worktree errors "not initialized for aw").
