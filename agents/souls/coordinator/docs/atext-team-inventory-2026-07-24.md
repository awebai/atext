# atext team — per-instance classification (reset prep)

Date: 2026-07-24. Owner: coordinator. Status: read-only inventory, NO teardown.
Scope: the atext team's own instances only. All on Juan's Mac, default tmux
socket (server 38840, shared with ac/main/tsm — see socket note).
All identities are **local, single-team** (no global boundary identities here).

| Instance | Active work | Branch | Dirty/Unpushed | Authority | Unharvested learning | Disposition |
|---|---|---|---|---|---|---|
| **coordinator** (me) | this reset prep; merge gate | main (checkout) | — | merge gate; blueprint publish via hestia team-auth | none pending | **preserve→reshape** — model retires the permanent generalist coordinator for per-stream local coordinators; my role is a reshape candidate |
| **developer** | none (aajs merged) | developer-default-aaae-7 | clean/pushed | none | `developer/memory/tmux-dogfooding-isolation.md` (uncommitted) | retire-candidate **after learning committed** |
| **developer-2** | none (aahn.4 merged) | developer-2-soul-profile-authority-fidelity | clean/pushed (merged) | none | none | retire-candidate |
| **developer-frontend** | authoring the operating-model + transition plan (ACTIVE) | atext-llms-control | only untracked uv.lock | transition-plan author | none | **preserve/drain** — mid-authoring; retire only when the transition plan is handed off |
| **operations** | none active | main (checkout) | — | **DEPLOY authority** (library/folio/naapp deploys; prod-DB read creds) | **5 files uncommitted**: awid-registry-incidents, log-awid-registry-503s, render-env-single-key-endpoint, tmux-kill-server-forbidden, MEMORY.md | **preserve authority + COMMIT learning first**; model → Hetzner supervised service (Hestia-class) |
| **reviewer** | none | main (checkout) | — | none | `reviewer/patterns/common-failure-patterns.md` (modified, uncommitted) | retire-candidate **after learning committed** |
| **reviewer-2** | none | main (checkout) | — | none | none | retire-candidate |
| **presenter-pi** | none | presenter-pi | clean/pushed | none | none | retire-candidate (pi runtime; stale-cache caveat noted 07-24) |

## The one real preservation item
Seven uncommitted soul-learning files across operations / developer / reviewer —
durable knowledge (much of it tonight's security/ops incidents) sitting in the
working tree, never committed. This is exactly the "promote durable learning
before retirement" gate. Nothing else is at risk: all worktrees are clean and
pushed; no active atext-scope claim is in flight (the active board is dominated
by other teams — aw-developer, ac-coordinator, developer-hardening — which is
itself the "atext is an umbrella" problem the model fixes).

## Decisions that require Juan
1. **Commit the 7 learning files.** Recommend waking operations / developer /
   reviewer to harvest+commit their own soul learning (harvest is the agent's
   job), OR I commit on their behalf. Either way, before any retirement.
2. **The aweb.ai agents are out of atext scope but currently unowned.**
   hestia/athena/iris/metis/sofia/aida/ama/rhea belong to the aweb.ai company
   team, but no company-coordinator instance is running to inventory them.
   Who owns their inventory?
3. **operations disposition** is an authority migration, not a plain retire —
   it holds deploy authority + prod-DB read creds; the model moves it to a
   Hetzner supervised service. Timing/how is Juan's call.
4. **coordinator (me) disposition** — the model retires the permanent generalist
   coordinator. My own role is a reshape/retire candidate; flagging it plainly.
