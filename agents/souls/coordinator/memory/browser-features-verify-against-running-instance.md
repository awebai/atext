---
name: browser-features-verify-against-running-instance
description: For browser-facing features, require verification via Playwright against a real running instance before ACK/merge — TestClient/static-server "verified" claims miss JS-level breakage.
metadata:
  type: feedback
---

Twice in the folio build, browser behavior that passed server-side tests was
broken in the actual browser:
1. M8's editable editor: a regex in a non-raw f-string emitted a literal
   newline into the editor JS -> SyntaxError -> the whole editor script died
   (empty textarea, dead Save). M8's e2e never drove the editor in a browser,
   so it passed review and shipped broken to prod.
2. The /preview rebuild: developer claimed the live preview "verified" but had
   only exercised the /preview endpoint via TestClient + a static file server
   with no /preview, so the preview couldn't actually update. Juan caught it.

**Why:** TestClient and server-render assertions don't execute the emitted
JS; a static/mock server isn't the running app.

**How to apply:** For any browser-facing feature (editors, live preview,
client interactivity), require the developer's "verified" to mean **Playwright
against a real running instance**, and the claim must match exactly what was
exercised. Push back on "verified" that rests on TestClient-only or a static
server. Bake a browser-level smoke into e2e (the folio editable e2e now drives
/preview over the wire). See [[verify-main-worktree-before-merge]].
