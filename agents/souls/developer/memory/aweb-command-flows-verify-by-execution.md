# Verify aweb command FLOWS by execution, not by reading schemas

When a page/skill/doc shows a sequence of `aw` commands as a user journey, the
sequence is only correct if it has been RUN end to end. Reading the manifest
(flag presence, flag surface, value semantics) proves each command is
schema-shaped — it does NOT prove the command runs, nor that the journey
composes.

Hard evidence from the library aafv landing:
- I twice assembled a "team adopts a profile then evolves it on the shelf" flow
  from verified individual verbs. Both were wrong: `aw team create` materializes
  agents from the PUBLIC catalog (a test asserts it must not touch the shelf), so
  the running agents were public-pinned; the real bridge was `aw team adopt`
  (shipped later in 1.32.3), and the loop closes with `aw team refresh`.
- `aw library propose` is schema-correct but could not run as a one-liner — the
  CLI rejects an object body param (interpret.go convertBodyValue); the aw e2e
  submits proposals via `aw id request POST /v1/proposals` instead. A
  schema-verified `aw library propose ...` panel would have shipped a command
  that does not run — and that same class of bug reached the published skills.

Rules:
- Before publishing a command JOURNEY, get it EXECUTED against a throwaway
  team/shelf and copy the sequence that actually ran. The aweb team can do this;
  ask for the executed transcript, not a schema answer.
- The best source of a real flow is the repo's e2e tests (they run the stack) —
  read `cli/go/e2e/*` and `test_*_e2e.py`, and heed their comments (they call out
  verbs they avoid because of bugs).
- A command a human copy-runs must be a human command. Agent-cert actions (e.g.
  an agent proposing) are described, not shown as copiable panels.

Relates to [[verified-means-running-instance]] and [[naapp-getting-started-invariant]].
