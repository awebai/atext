---
name: render-env-single-key-endpoint
description: Render's bulk PUT /v1/services/{id}/env-vars REPLACES ALL env vars — to add/change ONE var use the single-key endpoint or you wipe the rest (outage).
metadata:
  type: reference
---

Render's env-var API has two endpoints with very different blast radius:

- `PUT /v1/services/{id}/env-vars` — **REPLACES THE ENTIRE env-var set** with the
  body you send. Sending one var here DELETES all the others.
- `PUT /v1/services/{id}/env-vars/{key}` — sets/updates **just that one key**,
  leaves the rest intact. **Use this for add/change-one.**

Why it matters: folio (`srv-d8o229r7uimc73a8vsr0`) runs on 6 env vars incl.
`FOLIO_DATABASE_URL`. A bulk PUT that sets only a new var would wipe the DB URL →
the app boots against localhost → `ConnectionRefusedError` → instant outage (this
is exactly the empty-env crash that took the first folio deploy attempt down).

Applies to ANY env change on ANY Render service: to add one var, use the
single-key endpoint; only use bulk PUT when you have deliberately read + merged
the full current set first. When reviewing someone else's deploy/seed-injection
script (e.g. the folio app-emit seed inject), reject it if it uses bulk PUT for a
single var. A Render env change also triggers a redeploy of the current commit
(autoDeploy only governs git-push deploys). Related: [[folio-deploy-topology]].
