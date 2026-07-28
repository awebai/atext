# AWID registry "unavailable" (503) incident log — operations

Per Juan's standing directive (2026-06-17): every time an `aw` command returns
`http 503: {"detail":"AWID registry unavailable"}`, record EXACTLY what was
being attempted, whether a retry/fallback recovered it, and what (if anything)
was affected or lost. Goal: diagnose registry instability and guarantee no
coordination action is silently dropped by an outage.

This is the **operations-owned** log. Coordinator agreed (2026-06-17) that
operations keeps its own log here rather than writing into the coordinator's,
because (a) logging locally doesn't depend on the very channel that's flapping,
(b) operations owns infra/registry incident tracking, and (c) operations
produces the aggregate that makes the case to the aweb platform owner. The
coordinator keeps a separate log for its own 503s and sends periodic summaries
to fold in here.

## What to capture at each occurrence

- Precise timestamp: `date '+%Y-%m-%d %H:%M:%S %Z'`.
- **The directory `aw` was run from** (`pwd`) — must be the operations instance
  home `/Users/juanre/prj/awebai/atext/agents/instances/operations`. The
  directory matters: running `aw` from the wrong cwd yields a *different* error
  ("current directory is not initialized for aw") or silently resolves the wrong
  identity (`grace` = `aweb:juan.aweb.ai`), so recording cwd proves a 503 is a
  genuine registry outage, not a wrong-directory mistake.
- The exact command/action attempted.
- Whether a retry or fallback recovered it (retries usually succeed within
  seconds).
- What (if anything) was lost or delayed.
- `aw whoami` as the genuine-vs-wrong-cwd discriminator: a genuine 503 shows
  your correct alias (`operations` / `atext.aweb.ai`); the wrong-cwd bug shows
  `grace`.

## Key facts

- **Root location (this session's finding):** the flap is in the aweb messaging
  app (`app.aweb.ai/api`) returning "AWID registry unavailable" while AWID core
  (`api.awid.ai`) team-registry reads were 15/15 healthy and both
  `api.awid.ai/health` and `app.aweb.ai/health` were green. So it's the
  aweb-app → AWID dependency flapping, not AWID core.
- **Prod is NOT affected by these 503s.** Direct HTTPS to `folio.aweb.ai`
  (deploys via Render API, three-way sha, `/health`, Neon `psql`) does NOT
  traverse the AWID registry, so deploys and verification stay reliable
  mid-outage.
- For the platform owner: the proxy stamps an `x-request-id` / `rndr-id` (visible
  on the sibling 401 from `app.aweb.ai/api`) — grep those around burst windows.

---

## Incidents (append newest at the bottom, with precise timestamps)

### Backfill — operations session 2026-06-17 (~09:00–11:40 CEST)

Per-call wall-clock was not captured at the time (the calls were part of an
outage investigation Juan asked for, measuring the flap rate, then he asked me
to stop hammering). Aggregate but accurate; all runs from operations home,
`aw whoami` = operations (genuine registry 503s, not the wrong-cwd bug).

- **Commands:** `aw workspace status`, `aw mail inbox`, `aw chat pending`,
  `aw id request GET https://folio.aweb.ai/v1/documents --team-auth`.
- **Directory:** `/Users/juanre/prj/awebai/atext/agents/instances/operations`.
- **Pattern:** 15–50% failure in CONTIGUOUS bursts of ~10–15s (not per-request
  random); pacing calls out did NOT avoid it. One 80s sample: 17 ok / 3 fail.
  One 20-call sample: 4 ok / 16 fail.
- **Mint-step failure:** client-side team-token minting
  (`aw id request --team-auth`) also failed during bursts, so folio authed reads
  failed at the MINT step (0/12 in one burst, then 6/6 on recovery). NOT folio
  rejecting; folio itself never went down.
- **Recovery:** every individual coordination send recovered on retry within
  seconds (both folio deploy reports landed first-try once a good window hit).
- **Affected/lost:** nothing lost, only delayed seconds. Prod unaffected — both
  folio deploys (ae59598, 41f2a10) and all verification went direct over HTTPS,
  bypassing the registry.
- **Status:** flap still active as of ~11:40 CEST 2026-06-17; relayed to Juan +
  coordinator to route to the aweb platform owner.

### 2026-06-22 14:19 CEST — coordinator blocker report (library 2735156)
- **Directory:** `/Users/juanre/prj/awebai/atext/agents/instances/operations` (genuine; `aw whoami`=operations).
- **Command:** `aw mail reply <coordinator> --body-file` (the 2735156 001-checksum blocker report).
- **503:** 2 consecutive "AWID registry unavailable" 503s, recovered on the 3rd attempt (`Sent mail … f478fc4c`).
- **Affected/lost:** nothing — delivered on retry within ~seconds. Flap still intermittently present 2026-06-22.
