# A naapp's getting-started is ONE section: zero to the naapp's core value, minimum steps

Juan's invariant for every naapp landing (stated on the library aafv landing).

A naapp landing must NOT have a generic "stand up an aweb team" onboarding plus a
separate "here's what this app does" section — that reads as two half-answers and
buries the point. Instead there is a SINGLE getting-started that goes from zero to
having the thing the naapp is FOR, in the minimum number of steps. The
getting-started IS the naapp's value story.

For **library** that end state is a *shelf-based, self-improving team*: install aw
→ create the team → install the library plugin → start it → `aw team adopt` the
agents onto the team's private shelf → the agents propose as they work → you
approve (`aw library approve`) → `aw team refresh` applies the mint. The generic
"create a team + list-blueprints" flow is aweb.ai's story, not library's.

Corollaries proven the hard way on this landing:
- Every command shown as a copiable panel must be one a human actually RUNS.
  A proposal against the shelf is framed actor-neutrally ("a proposal is
  submitted … you approve") and shown as description, not a panel — an agent
  proposing is not the reader's copy-run step, and the published profiles do not
  yet propose autonomously (a copy flip waits on that becoming true). NOTE: the
  `aw library propose` verb DOES run as a one-liner (with `--content`, never the
  silently-broken `--body-file`); it is described, not panelled, by editorial
  choice, not because it cannot run. See [[aweb-command-flows-verify-by-execution]].
- Don't ship the step ORDER on a guess; the end-to-end sequence must be verified
  by EXECUTION against a throwaway shelf, not by reading the manifest schema.
