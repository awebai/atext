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
  `aw library propose` is the *agent's* autonomous action (team cert), not a
  human copy-run step — so it is described, never panelled. This also dodged a
  CLI verb that could not run as a one-liner. See [[aweb-command-flows-verify-by-execution]].
- Don't ship the step ORDER on a guess; the end-to-end sequence must be verified
  by EXECUTION against a throwaway shelf, not by reading the manifest schema.
