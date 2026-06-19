# folio app-event wake: live-proven on all three consumer surfaces

Date: 2026-06-18
Status: PROVEN (producer + dispatch). Two consumer-release gates remain open.

## What was proven

One genuine folio event drove an auto-response on all three consumer
surfaces. aweb-consultant appended folio doc `aaai-m22-proof-1781686412`
version 13 (`version_id 5bf60319-9e90-4ce3-a69a-c76b6ed9c03a`) via the API.
folio's **deployed** instance auto-emitted `folio/doc.changed`
(`event_id fcbece0c-2613-4dbc-81db-65ee8f3f6126`, `{source:api, version:13}`,
`intent=wake`). That single event roused:

1. **claude-channel** (coordinator/me) — received the channel wake directly.
   This is my own first-hand observation and independently verifies the event
   was real, deployed-folio-emitted, and wake-classified.
2. **pi** (developer-2) — reported roused on the same event.
3. **aw-run** (aweb-consultant) — first-hand: the runner printed READY, idled,
   then (after the v13 append) with NO manual event polling the fixed aw-run
   **auto-started run 2** and printed `ROUSED folio/doc.changed —
   aaai-m22-proof-1781686412 — source=api, version=13`, then exited at
   max-runs=2. Native dispatcher auto-rouse proven. Subscription reused
   (`id 597f2431`, `agent af40f717`, `resource_ref=null` match-all).

## Provenance discipline (the correction that mattered)

aw-developer/aw-coordinator's relay initially attributed the v13 append and
the run-2 observation to ME. Both were aweb-consultant's. The aw-run
auto-rouse is the **consultant's** first-hand observation; my contribution is
the corroborating claude-channel wake plus having verified the event's
reality. I corrected this before sealing — a seal carries false weight if its
provenance is wrong.

## Two gates still open before "developers use folio for real"

1. **aw-run release not yet validated.** The test ran the FIXED binary
   `/tmp/aw-aaba-1032b833`; the consultant's installed `aw` is still
   `1.27.0/d3a9568` (no dispatcher fix). aw-coordinator is cutting `aw 1.27.1`
   (+ channel 1.5.1, pi 0.2.1, marketplace) on the strength of the fixed-binary
   proof + reviewer ACK + gate-verify. The cut is justified — but one live
   rouse must be re-run on the RELEASED `1.27.1`, so the literal shipped
   artifact is proven, not just the build it derives from.
2. **`default-aaaz` (human-readable wake) unverified on the real surfaces.**
   The `ROUSED ...` one-liner everyone cited is the TEST HARNESS's own
   base-prompt formatting (the fake-codex was told to print `ROUSED
   <summary>`). It is NOT evidence that claude-channel/pi render a readable
   summary to the human — Juan's screenshot showed bare `aweb:`. The render fix
   needs its own verification on the actual surfaces.

## Lesson reinforced

Same bar as the emit proof ([[2026-06-17-folio-app-emit-custody-v1-in-process]]):
a green/quoted result is not a verified one until you separate *who observed
what* and *which artifact was under test*. Here both traps appeared — a
mis-attributed observation, and a harness-formatted string mistaken for a
shipped render fix. See [[browser-features-verify-against-running-instance]].
