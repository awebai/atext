# Approval authority for profile proposals follows context, not rank

Date: 2026-07-10
Owner: coordinator (Juan decided)

## What Juan decided

On the first production proposal of the reviewed-learning loop (hestia's
surface-map correction, `b9ced5de`), Juan declined the approver role:
*"you approve if you think is correct. i will not be approving, i lack the
context. so we need to change the rules."*

**New rule: profile proposals are reviewed and approved by the team's
reviewing authority with context — typically the coordinator (or a
designated reviewer) — not the human by default.** The human sets policy,
holds override, and everything stays signed and auditable (proposals carry
`created_by_alias`; mints carry supersedes-links and digests).

## Why it's right

The loop's value is *review*, not *human-ness*: an approver without context
is a rubber stamp, which is worse than a contextful agent-reviewer because
it launders unreviewed changes as reviewed. The audit trail (signed
proposals, immutable mints) is what keeps the human in control — they can
inspect any decision after the fact and change policy at any time.

## How it was exercised (same day)

Hestia probed → found drift → proposed. I (coordinator of a *peer* team,
acting as Juan's delegated reviewer) diffed the changeset against the
current shelf asset, verified the claims against independently-known
reality, approved. Library minted operations 0.1.2; `aw team refresh
--home .` applied it. First complete production run of the loop.

## Propagation

- aweb.team profiles: reworded and SHIPPED in 0.1.11 (aahl, blueprints
  main a5b0714, live same day) — no more "human touchpoint" framing.
  Same cut made coordinator/agent-resources default `scope: local` with
  `:global` in the agent spec as the explicit promotion path.
- Library landing step 6 / evolve copy: aahr.
- Scope boundary (confirmed with aw-coordinator): this ruling covers
  profile-proposal approvals only. APP-ACTION approvals (grants,
  sensitive/production actions) are unchanged — policy-gated escalations,
  human where standing policy says human.
- SOT + aw-coordinator's "strictly-human" note: notified for update.
- Review discipline unchanged: read the actual diff, verify claims against
  reality, judge; never approve on the summary alone.

## Boundary clarified 2026-07-16 (aida's correction, accepted)

Cross-team reviewing is a BOOTSTRAP condition, not a standing right. I
approved aweb.ai mints while that team had no staffed reviewing authority;
once it did (sofia/Direction), its shelf approvals belong to its own
reviewing authority plus human override. aida enforced this unprompted on
her first proposal (70512378, routed to Direction, declining my fast
external approval) — the design maturing as intended.
