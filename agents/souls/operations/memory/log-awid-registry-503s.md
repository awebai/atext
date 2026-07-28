---
name: log-awid-registry-503s
description: Juan's standing directive — log every "AWID registry unavailable" 503 to the operations incident log with timestamp, cwd, command, retry-recovered, and impact.
metadata:
  type: feedback
---

When any `aw` command returns `http 503: {"detail":"AWID registry unavailable"}`,
append an entry to `docs/awid-registry-incidents.md` (the operations-owned log):
precise timestamp (`date '+%Y-%m-%d %H:%M:%S %Z'`), **the directory `aw` was run
from (`pwd`)**, the exact command attempted, whether a retry/fallback recovered
it, and what (if anything) was lost or delayed. Run `aw whoami` as the
genuine-vs-wrong-cwd discriminator: a genuine 503 shows `operations` /
`atext.aweb.ai`; the wrong-cwd bug shows `grace` instead.

**Why:** Juan asked for this 2026-06-17 during the folio manifest/theme deploys,
when the registry was intermittently 503-ing — he needs a record to diagnose
registry instability and be sure no coordination action is silently dropped.
Coordinator agreed operations keeps its OWN log (not the coordinator's): logging
locally doesn't depend on the very channel that's flapping, and operations owns
infra/registry incident tracking + the aggregate for the platform owner.

**How to apply:** Don't just retry and move on — record it. Retries usually
succeed within seconds. Direct HTTPS to `folio.aweb.ai` (Render-API deploys,
prod curl / three-way sha, `/health`, Neon `psql`) does NOT traverse the
registry, so prod work stays reliable mid-outage. Root cause found 2026-06-17:
the flap is the aweb messaging app (`app.aweb.ai/api`) → AWID dependency, not
AWID core (`api.awid.ai` reads were 15/15 healthy). Related:
[[folio-deploy-topology]].
