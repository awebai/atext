# Measure conditions, not counts — grep tallies are blind to behaviour

Learned 2026-07-27 during the channel-flapping investigation, over four
inflated first-results in one night (all caught before publication).

**The rule:** raw text search counts OCCURRENCES. Questions about behaviour
are questions about CONDITIONS. When asking "does this build do X?",
extract the deciding expression — the guard and the configured value — not
a tally of call sites.

**The case that proves it.** Three channel builds differ in whether they
acknowledge mail. All three have exactly 2 ack call sites, so counting was
blind *by construction*. Extracting the guard and config settled it in one
command each:

| build | guard | config | behaviour |
|---|---|---|---|
| 1.4.12 | *(none)* | *(none)* | acks unconditionally — predates the guard |
| 1.5.2 | `!== "manual"` | `"manual"` | guard false → **never acks** |
| 1.6.0 | `!== "manual"` | `"delivery"` | guard true → acks |

**The other three traps of that night, same family:**
- Counting `message_id` per line counted MY OWN `aw mail reply <id>` tool
  calls as inbound deliveries → reported 1369 redeliveries; real answer 8.
  Filter to the actual channel tag, user-role only.
- Transcript records each stream event TWICE (one with uuid, one without).
  Dedupe by record uuid or halve everything.
- A null from an instrument that cannot report the thing is not evidence of
  absence: 1.4.12 emits no `stream_state` at all, so "zero drops on Hetzner"
  measured nothing. **Always check the instrument can see the phenomenon
  before believing a clean negative.**

**Bonus pattern worth reviewing for:** the 1.5.2 defect was the COMBINATION
of a guard and a config value introduced together — neither wrong alone,
which is why it passed review. Review introduced-together pairs as a unit.

**How to apply:** before reporting any measurement, ask (1) could this count
include my own actions? (2) does the source double-record? (3) can the
instrument observe the thing at all? (4) am I counting when I should be
extracting a condition? See [[published-commands-verified-by-execution]] —
same discipline, different layer.
