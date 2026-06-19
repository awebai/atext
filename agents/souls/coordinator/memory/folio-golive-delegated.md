---
name: folio-golive-delegated
description: Juan delegated folio go-live authority to the coordinator (2026-06-15); deploy needs no separate human confirm.
metadata:
  type: project
---

On 2026-06-15 Juan said "go live without waiting for me. folio.aweb.ai is
already pointing at the render project." This **delegates the folio
production go-live to the coordinator** — operations deploys on the
coordinator's commit hand-off, without a separate human green light. The
domain `folio.aweb.ai` is already attached to the Render service on Juan's
side.

Scope/reading: this removes the *approval gate*, not Juan's explicit
"deploy the full epic (M3+M6)" timing choice made minutes earlier. So:
ship the complete epic autonomously when M3+M6+squash are all on main.
Operations still must smoke-check before promoting and hold on a failing
check. This delegation is folio-specific; the broader confirm-first rule
for risky changes (auth, data, billing, other deploys) still stands.
See [[folio-greenfield-single-migration]] is in decisions/.
