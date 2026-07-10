# AWID registry "unavailable" (503) incident log

Per Juan's directive (2026-06-17): every time an `aw` command returns
`http 503: {"detail":"AWID registry unavailable"}`, record EXACTLY what was
being attempted, whether a retry/fallback recovered it, and what (if anything)
was affected or lost. Goal: diagnose registry instability and guarantee no
coordination action is silently dropped by an outage.

At each occurrence capture: a precise timestamp
(`date '+%Y-%m-%d %H:%M:%S %Z'`) AND the directory `aw` was run from (`pwd`).
The directory matters: running `aw` from the wrong cwd yields a *different*
error ("current directory is not initialized for aw"), so recording cwd proves
a 503 is a genuine registry outage and not a wrong-directory mistake. `aw` must
be run from the coordinator instance home
(`/Users/juanre/prj/awebai/atext/agents/instances/coordinator`); the Bash tool
resets cwd there after every call.

Direct HTTPS to folio.aweb.ai (e.g. prod curl) does NOT go through the AWID
registry, so prod verification stays reliable during these outages.

Log created: 2026-06-17 10:45 CEST. **All incidents below were run from the
correct home `/Users/juanre/prj/awebai/atext/agents/instances/coordinator`
(no `cd` issued) — i.e. genuine registry 503s, not wrong-directory errors.**

---

## Backfilled incidents from this session (exact wall-clock not captured at the time)

### Incident 1 — theme-design approval to developer-frontend
- **Command:** `aw chat send-and-wait developer-frontend "APPROVED — proceed... (manifest-update catch)"`
- **Directory:** `/Users/juanre/prj/awebai/atext/agents/instances/coordinator` (correct home)
- **Error:** `connecting to SSE: aweb: http 503: {"detail":"AWID registry unavailable"}` — the SSE *wait* stream failed.
- **What I did:** re-sent the identical message via `aw chat send-and-leave developer-frontend` (fire-and-forget, no SSE wait). It SUCCEEDED ("Message sent to developer-frontend").
- **Affected/lost:** nothing. The approval + the "update src/folio/aweb-app.json so theme-set gains preset" instruction was delivered. Only the blocking reply-wait was skipped.

### Incident 2 — team-state checks after Juan asked about the deploy
- **Commands:** `aw workspace status` (came back empty through a grep) and `aw mail inbox` → `aweb: http 503: {"detail":"AWID registry unavailable"}`.
- **Directory:** `/Users/juanre/prj/awebai/atext/agents/instances/coordinator` (correct home)
- **What I did:** retried `aw workspace status` 3x, then ran it raw — it RECOVERED and returned the full roster (revealing operations was offline). `aw mail inbox` subsequently returned "No messages" normally.
- **Affected/lost:** nothing lost; brief (~seconds) blindness to team state. The 503 transiently hid that operations had gone offline.

### Incident 3 — "manifest LIVE" ping to aweb-coordinator
- **Command:** `aw mail reply b3986485... "LIVE. ...three-way sha verified..."`
- **Directory:** `/Users/juanre/prj/awebai/atext/agents/instances/coordinator` (correct home)
- **Error:** `aweb: http 503: {"detail":"AWID registry unavailable"}` (exit 1).
- **What I did:** retried in a loop; SUCCEEDED on the first retry (`Sent mail ... message_id=2fb58bfd-b7c3-4b50-8d71-e2f3a3aad15e`). The aw-developer fixture-handoff mail and the operations chat in the same batch had succeeded on first try.
- **Affected/lost:** nothing. The live ping was delivered on retry.

---

## Genuine registry 503 vs. the repo-root identity bug (aweb-coordinator, 2026-06-17)

aweb-coordinator + aw-coordinator hit coordination failures that **looked like
registry flakiness but were not**: running `aw` from the monorepo/repo ROOT
resolves the wrong identity (`grace` = `aweb:juan.aweb.ai`) instead of the
instance home. Symptom: `agent not found` on teammates' aliases + messages
**sent as the wrong identity**. Fix: always run `aw` from the instance home;
never batch `git` (repo root) + `aw` in one shell.

**These are two different failures** — record which one each incident is:
- **Repo-root identity bug:** `agent not found` / wrong-identity send. Cause:
  wrong cwd. Discriminator: `aw whoami` shows `grace`, not your alias. Fix: cd
  to instance home.
- **Genuine registry 503:** literal `http 503: {"detail":"AWID registry
  unavailable"}`. Cause: server-side registry unavailable. Transient, recovers
  on retry. `aw whoami` shows your correct alias.

Confirmed 2026-06-17 10:58 CEST: `aw whoami` = `coordinator` / `atext.aweb.ai`
(NOT `grace`) from `/Users/juanre/prj/awebai/atext/agents/instances/coordinator`.
So all three backfilled incidents are **genuine registry 503s**, not the
identity bug.

---

## Root cause (operations investigation, 2026-06-17, ~09:00–11:40 CEST)

operations (whoami=operations, from home — genuine 503s) investigated the flap
at Juan's request. Findings:
- Flap is **contiguous bursts of ~10–15s**, 15–50% failure within a burst (not
  per-request random); pacing calls out does NOT avoid it. Samples: 17 ok/3 fail
  over 80s; 4 ok/16 fail over 20 calls.
- Team-token minting (`aw id request --team-auth`) also failed in bursts → folio
  authed reads failed at the **mint step** (0/12 in a burst, 6/6 on recovery).
  NOT folio rejecting; folio never went down.
- **Root location:** the aweb messaging app (`app.aweb.ai/api`) returns "AWID
  registry unavailable", while the AWID core (`api.awid.ai`) read **15/15
  healthy** and both `/health` endpoints were green. So it's the
  **aweb-app → AWID dependency flapping, not AWID's core.**
- Recovery: every needed send succeeded on retry within seconds; nothing lost.
- **Prod impact: NONE** — direct HTTPS to folio.aweb.ai (deploys, three-way sha,
  /health, Neon) does not traverse the registry.
- Action for the aweb platform owner: check `app.aweb.ai/api` logs (grep the
  `x-request-id` / `rndr-id` the proxy stamps) around the burst windows.

operations keeps its OWN incident log in the operations soul; this coordinator
log holds my 503s + the consolidated root cause above. Both surface to Juan.

---

## Ongoing incidents (append newest at the bottom, with precise timestamps)

### Incident 4 — Library epic lookup while scoping default-aaas.14
- **Timestamp:** 2026-06-18 23:49 CEST (the failing call was moments earlier, same minute)
- **Command:** `aw task show default-aaas.14` (and `aw task list --parent default-aaas.14`)
- **Directory:** `/Users/juanre/prj/awebai/atext/agents/instances/coordinator` (correct home; `pwd` confirmed)
- **Error:** `getting task default-aaas.14: aweb: http 503: {"detail":"AWID registry unavailable"}`
- **What I did:** retried `aw task show default-aaas.14` once — it RECOVERED and returned the full epic. (Separately, `--parent` is not a valid `aw task list` flag — that's a CLI-usage error, not a 503.)
- **Affected/lost:** nothing. The epic loaded on the first retry; genuine transient registry 503.

### Incident 5 — kicking chunk A (model-v2) review + e2e
- **Timestamp:** 2026-06-19 11:21 CEST
- **Command:** batch of three — `aw mail send --to reviewer` (chunk A review brief), `aw mail send --to developer-2` (full .14.9 e2e), `aw task comment add default-aaas.14.2`. All three returned `http 503: {"detail":"AWID registry unavailable"}` on the first attempt.
- **Directory:** `/Users/juanre/prj/awebai/atext/agents/instances/coordinator` (correct home; `pwd` confirmed)
- **What I did:** retried each in a bounded loop (no sleep; foreground sleep is blocked). All three SUCCEEDED on retry — reviewer mail (baca8ca3), dev-2 mail (9a5bf0cc), board comment.
- **Affected/lost:** nothing. Genuine transient registry 503; recovered within the retry loop.

### Incident 6 — decrypting an inbound ac-developer-2 chat message
- **Timestamp:** 2026-06-19 17:47 WEST
- **Command:** the channel's auto-decrypt of an inbound encrypted chat (`aw chat history --session-id c0e36aaf... --message-id ab69bf6d... --json`) failed with `http 503: {"detail":"AWID registry unavailable"}` — so the message arrived `decrypted=false`.
- **Directory:** `/Users/juanre/prj/awebai/atext/agents/instances/coordinator` (correct home; `pwd` confirmed)
- **What I did:** retried `aw chat history` for that message in a bounded loop — RECOVERED on retry; read the plaintext (a routine ac-developer-2 ack, nothing actionable).
- **Affected/lost:** nothing. Genuine transient registry 503 on the inbound decrypt path; recovered on retry. NOTE: this is the first 503 observed on the message-DECRYPT/read path (prior incidents were on sends) — same registry flap, just surfaced as `decrypt_error` on an inbound; the fix is the same (retry).
