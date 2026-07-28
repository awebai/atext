# Agent-team operating model

Status: implementation-preparation draft, revised for multi-host operation  
Date: 2026-07-24  
Decision owner: Juan  

## Purpose

Define a coherent way for Juan, CJR, GreaterSkies/Thestarmaps, aweb.ai,
the aweb and AC development teams, and the naapps to work with AI agents.

The immediate problem is not a shortage of agents, roles, profiles, or
coordination mechanisms. It is that several distinct things have become
conflated:

- a role or profile;
- a durable expert;
- a running instance;
- a chat session;
- a tmux window;
- an aweb identity;
- a team;
- a repository;
- a product or company function;
- a host.

The result is a large collection of agent homes, identities, windows,
handoffs, status files, and task claims without one reliable view of what
is alive, what matters, what is blocked, and what has actually been learned.

This proposal separates those concerns and assigns each existing system one
clear responsibility.

## Executive proposal

Use:

- **OAS** as the execution and learning layer;
- **aweb** as the identity, messaging, task, and cross-machine coordination
  layer;
- **a constrained host dispatcher** as the bridge from signed, durable work
  requests to local OAS lifecycle operations on each machine;
- **Library** as the signed distribution and governed evolution layer for
  proven agent roles;
- **Git and project source-of-truth documents** as the durable authority for
  product facts, decisions, runbooks, and local expert knowledge;
- **tmux** only as an OAS-controlled runtime console, never as the
  organizational model.

The governing rule is:

> Keep responsibility and knowledge durable. Make execution disposable.

A durable soul may exist without a running process. A durable identity may
exist without a running process. A profile in a catalog does not imply a
staffed role. Only work that has a current outcome, owner, trigger, and queue
justifies a live agent instance.

Host placement is not determined by how long a role exists. It is determined
by what the current instance needs:

- direct conversation with Juan, visible browser work, or private local data
  belongs on Juan's computer;
- uninterrupted event handling and batch work belong on Hetzner;
- specialized computers join as capability-specific workers;
- a soul remains portable even though each instance runs on exactly one host.

## Evidence from the current systems

### CJR

The CJR design contains several good principles:

- one KB for Juan's world rather than per-channel memories;
- specialists as modes;
- one coordinator;
- local-only handling of private and financial documents;
- deterministic tools for exact work;
- review proportional to risk.

The implementation works against those principles by materializing the whole
seven-role roster and providing a launcher that creates one tmux window per
role. The catalog of possible responsibilities becomes the running team.

There is little evidence yet that all seven standing instances compound:
the durable role memories currently contain only a few substantive notes.
That does not mean the roles are wrong. It means a soul catalog and a live
roster must be different things.

Sources:

- `~/cjr/agents/docs/team-architecture.md`
- `~/cjr/kb/kb-sot.md`

### GreaterSkies / Thestarmaps

TSM contains the strongest evidence of real agent learning.
`agents/instances/zeus/knowledge/LEARNINGS.md` records precise rules derived
from actual incidents, including:

- the worktree is not the deployment;
- external systems must be tested with positive, negative, and sameness
  controls;
- metered spend must be bounded in code;
- recurring jobs process their delta rather than rerolling history;
- a number without its underlying finite list is not a durable record;
- task comments are canonical state, but the next actor must also be woken.

Those lessons changed later work. This is the learning standard to preserve.

The structural problem is that Zeus combines:

1. program coordinator;
2. keeper of institutional knowledge;
3. sole privileged production operator.

That forces the project's heartbeat and its production credentials onto the
same local machine and identity. The useful knowledge is also largely trapped
inside an ignored instance home while the committed team description records
a different roster.

Sources:

- `~/tsm/AGENTS.md`
- `~/tsm/docs/source-of-truth/team.md`
- `~/tsm/agents/instances/zeus/knowledge/LEARNINGS.md`

### aweb.ai company team

The `ai.aweb` model has a strong artifact vocabulary:

- active work belongs in tasks;
- current published state belongs in status;
- restart context belongs in a handoff;
- direction changes belong in decision records;
- release claims require verified-live evidence;
- substantial work benefits from a second perspective.

The six-peer operating model does not reliably move the company. Direction
has been offline for an extended period; Product and Outreach state became
stale; the weekly roll-up stopped; Operations often had nothing in flight;
and a valid Support learning proposal waited because the designated reviewing
authority was absent.

"Jointly responsible" diluted the one responsibility that matters most:
someone must continuously decide what the company is trying to accomplish
and ensure the next action happens.

Sources:

- `~/prj/awebai/ai.aweb/docs/agent-first-company.md`
- `~/prj/awebai/ai.aweb/docs/team.md`
- `~/prj/awebai/ai.aweb/status/`

### Current development teams

The simple coordinator → developer → reviewer pattern is sound. Its current
deployment is not:

- work for aweb, AC, atext, and Library appears on one atext team board;
- stale claims survive for weeks;
- long-lived generalist developer contexts accumulate obsolete conversations;
- agent homes and tmux windows are created and retired manually;
- unrelated teams have shared a tmux failure domain.

In the coordinator's 2026-07-24 report, a clean developer plus a clean
adversarial reviewer dedicated to one security epic was substantially more
effective than accumulated generalist instances. The pair caught key-loss
and identity-spoof risks that fast green review had missed.

The required review model is:

1. one fresh, domain-appropriate reviewer proves the epic's change;
2. the coordinator performs an integration check at merge:
   - the reviewed SHA is the merge tip;
   - findings were actually resolved in code;
   - the complete branch range is coherent;
   - appropriate fleet or live dogfood passes.

This is not two review ceremonies and does not require a permanent reviewer
instance.

Runtime is part of staffing. In the same security work, the selected
Pi/Codex runtime could not perform the adversarial review, while Claude could.
Runtime must therefore be selected from the task's domain and permissions,
not treated as an interchangeable launch option.

The current multi-host team also reveals a clean architectural boundary.
According to the coordinator's 2026-07-24 operational report:

- aweb mail/chat, the task board, roster presence, Git branches, exact-SHA
  handoffs, independent review, merge gates, and live-URL verification work
  across hosts;
- spawning, placement, tmux, process inspection and recovery, and browser
  visibility remain host-local and manual;
- seven agents were manually ported to Hetzner in one session;
- a coordinator could see a remote agent go offline but could not recover its
  process;
- three tmux-server failures had to be repaired separately on the affected
  machines.

The coordination plane is therefore substantially working. The missing
system is a narrow, host-agnostic lifecycle plane. It should extend OAS rather
than replace aweb coordination.

## System responsibilities

### OAS: execution and local learning

OAS owns:

- committed souls;
- disposable instances;
- sessions and resumption;
- work modes (`worktree`, `checkout`, `attached`, `workspace`);
- runtime and model selection;
- exact capability composition;
- spawn and retirement hooks;
- instance working state;
- observation capture and knowledge harvest.

OAS should be the normal internal mechanism for starting and ending agent
work. Repository-specific instance scripts and aweb's simpler team launcher
remain compatibility or onboarding paths, not the primary internal runtime.

OAS is currently a single-host executor. `oas spawn` creates an instance and
launches it in tmux on the machine where the command runs. `oas status --team`
can discover local sibling repositories, and `oas aweb roster` can list
members across machines, but neither remotely starts or recovers a process.

OAS must run with isolated per-deployment tmux sockets and sessions. A
distinct session alone does not contain a `tmux kill-server` failure. OAS
also needs explicit session states—running, dormant, failed, restarting—
separate from the continued existence of an instance directory or tmux
window.

Hetzner service agents need a reboot/recovery supervisor; tmux persistence
alone is not a service guarantee. "Always on" means reachable, event-driven,
restartable, and monitored. It does not mean that a model must continuously
generate or that an unattended tmux shell proves the service is healthy.

### Host dispatcher: cross-machine lifecycle

Each worker machine should run a small deterministic host service—working
name `oas-host`—that translates authorized structured requests into local
OAS operations.

The dispatcher owns:

- verifying the requesting identity and its authority;
- checking allowlisted teams, repositories, souls, runtimes, and operations;
- choosing among the capabilities available on its host;
- allocating globally unique instance and branch names;
- fetching the relevant repository and exact base revision;
- invoking local OAS spawn, status, interrupt, resume/restart, and retire;
- reporting instance identity, host, branch, and lifecycle state;
- capacity limits, audit records, and failure reporting.

A spawn request should be data, not a shell command:

```yaml
team: ac
task_id: default-aajm
soul: developer
host_class: hetzner-general
base_sha: 1234abcd
requested_by: ac-coordinator
```

The dispatcher must never accept arbitrary commands from a message. It should
be a thin adapter around OAS, not an LLM persona and not a new coordination
system. An initial pilot may carry this exact request over a constrained SSH
command. The durable transport should be an authenticated aweb request tied
to the owning task.

If OAS later gains native remote lifecycle support, it can replace this
adapter without changing the work, identity, task, or evidence model.

### aweb: coordination and authority

aweb owns:

- local and global agent identities;
- team membership and certificates;
- revocation;
- cross-machine and cross-team addressing;
- mail and chat;
- shared tasks and claims;
- event delivery and wake signals;
- the cross-machine roster.

The OAS aweb integration must distinguish two identity lifetimes:

- **durable identities**, such as Merlin, Minerva, Aida, and Hestia, are
  adopted into an OAS instance without changing their keys or authority and
  are never deleted merely because one instance is retired;
- **task-scoped identities**, such as ordinary developers and reviewers, may
  be minted at spawn and revoked at retirement.

Spawn must fail closed if enrollment, team binding, or post-spawn
verification fails. A warning followed by a nominally successful spawn is
not safe enough for coordinated work.

A global identity is a durable address and authority decision. It does not
imply a permanently running process. Ordinary task workers and reviewers
should normally use local team identities.

The aweb-specific OAS adapter is an aweb-owned package in the aweb monorepo,
following the same ownership pattern as the Pi adapter. Generic lifecycle
improvements belong upstream in OAS. The adapter owns:

- aweb identity adoption, minting, verification, and retirement semantics;
- aweb messaging composition;
- an aweb task/work layer that uses the existing `tasks.aweb.ai` application
  rather than inventing another task system.

Remote host dispatch is a later layer over this seam, not part of its first
release.

### Library: cross-boundary role distribution

Library owns:

- public role releases published by an AWID team;
- immutable versions and content digests;
- private team shelf variants;
- provenance;
- governed profile proposals;
- reviewed minting and explicit refresh.

Library does not own:

- running processes;
- worktrees;
- tmux;
- local instance state;
- general memory storage;
- general skill or capability packaging;
- fleet supervision.

The complete Library value path is:

1. publish a signed profile;
2. fetch and verify publisher plus digest;
3. import it to a team's private shelf if desired;
4. materialize or adapt it for a runtime;
5. propose a profile-asset improvement;
6. have a contextful reviewing authority evaluate it;
7. mint a new version;
8. refresh deliberately.

Standalone Library proposal targets for `memory`, `skill`, and `workflow`
should not exist. Those concerns belong inside a profile or in OAS capability
packages. Library should fail closed when asked to approve an unsupported
target.

### Git and project sources of truth

Git remains the authority for:

- project architecture and operational reality;
- product decisions;
- company decisions;
- runbooks;
- local souls;
- reusable skills owned by the project;
- reviewed learning before it becomes a published role release.

Library is a release/distribution surface, not a replacement for reviewable
source.

## Three kinds of residence

Asking where an agent lives has three different answers:

1. **Durable home:** the committed soul in the repository that owns the
   agent's responsibility.
2. **Execution home:** the machine-local instance directory and worktree for
   one piece of active work.
3. **Coordination address:** the aweb team or global identity through which
   the instance can be reached.

The authoritative soul lives in Git rather than on one favored computer.
Every authorized host may have a clone. Instance homes, logs, worktrees,
runtime credentials, and sessions remain local to the host and are normally
gitignored.

The canonical future layout should follow OAS directly:

```text
<owning-repo>/agents/<soul-name>/soul/
<owning-repo>/agents/<soul-name>/instances/<instance-name>/
```

Examples:

```text
~/cjr/agents/merlin/soul/
~/cjr/agents/merlin/instances/merlin-desk/

~/tsm/agents/zeus/soul/
~/tsm/agents/frontend-developer/soul/
~/tsm/agents/reviewer/soul/

~/prj/awebai/ai.aweb/agents/aida/soul/
~/prj/awebai/ai.aweb/agents/hestia/soul/
~/prj/awebai/ai.aweb/agents/company-coordinator/soul/

~/prj/awebai/aweb/agents/developer/soul/
~/prj/awebai/ac/agents/reviewer/soul/
~/prj/awebai/library/agents/frontend-developer/soul/
```

On Hetzner, relevant repositories should be cloned under the same paths
relative to `~`. For example:

```text
~/prj/awebai/library/agents/developer/instances/developer-lib123-hz/
```

may exist only on Hetzner, while the corresponding committed soul exists in
both the Hetzner and local clones. A frontend incarnation of another soul
may exist only on Juan's computer:

```text
~/prj/awebai/library/agents/frontend-developer/instances/frontend-lib124-altair/
```

The existing `agents/souls/...`, `agents/instances/...`, TSM instance
worktrees, and mixed `ai.aweb/agents/<name>` layouts are earlier generations.
They should be treated as migration inputs, not rearranged en masse.

CJR is local-only by default. Its repository and private KB should not be
cloned to Hetzner merely for architectural symmetry. Each host receives only
the repositories and credentials needed by its allowed work.

Library profiles are not live souls and do not have instance directories.
They are reusable starting packages. Materializing a profile creates or
updates a soul in the repository that owns the responsibility; that soul
then develops project-specific knowledge. Only reviewed, generalizable
improvements flow back to Library.

## Host classes and placement

Machines are capability pools, not team owners.

| Host class | Capabilities | Default work |
|---|---|---|
| `local-interactive` | Juan present, direct conversation, headed browser, local/private data | Merlin, coordinators, frontend development, private CJR work |
| `hetzner-general` | uninterrupted Linux runtime, network reachability, concurrency | backend development, tests, reviewers, batch work |
| `hetzner-service` | supervised event listeners, restricted service credentials | Aida, Hestia, other genuinely always-reachable roles |
| specialized computer | host-specific browser, GPU, account, network, or hardware | only tasks declaring that requirement |

Place an instance by asking, in order:

1. Must it react while Juan's computers are off? If yes, use a supervised
   service host.
2. Must Juan converse with it frequently or watch the UI? If yes, run it
   locally.
3. Does it require private local data or local credentials? If yes, keep it
   local unless a separately authorized enclave exists.
4. Does it require production credentials? If yes, use the restricted
   operations environment, not the general worker pool.
5. Is it reproducible batch, backend, test, or review work? If yes, prefer
   Hetzner.
6. Does it require a specialized machine capability? If yes, dispatch to a
   registered host with that capability.

No persistent identity should run concurrently on two hosts. A soul may have
multiple task instances, but a stable service identity such as Aida or Hestia
has one active runner. If a role truly needs both an interactive and a
service presence, use two explicitly named instances with different
authorities rather than pretending they are one process.

Host location must come from live instance metadata and the aweb roster, not
handoff prose. Current documents already demonstrate why: Aida's 2026-07-13
handoff says Athena is on `altair.local`, while Athena's own 2026-07-13
handoff says Hetzner is her only runner.

The operator should maintain a small private host registry containing:

- stable host ID and current connectivity;
- host class and available runtimes;
- authorized teams and repository roots;
- browser and other special capabilities;
- credential class;
- concurrency and resource limits;
- dispatcher and supervisor health.

It contains no secrets. Secrets remain in host-native secret storage and are
made available only to the instances authorized to use them.

## OAS–Library integration

Library itself should not be an OAS capability. An aweb-owned adapter—working
name `oas-aweb-library`—should connect them.

The adapter should:

1. fetch a Library profile;
2. verify the profile digest and publishing team;
3. record the exact Library source pin;
4. project the role into an OAS soul or soul scaffold;
5. keep OAS deployment capabilities separate from portable role content;
6. optionally publish a reviewed soul release back to Library.

The semantic mapping is:

| Library | OAS |
|---|---|
| profile mission and instructions | soul instructions |
| profile-private skills | soul-private skills |
| templates and durable role artifacts | soul knowledge/templates |
| runtime assumptions | validated deployment requirements |
| profile version and digest | external source pin |
| team-private shelf variant | locally evolved soul lineage |
| OAS capabilities | not copied into the profile unless they are intrinsic to the role |
| instance handoff, state, logs | never Library content |

OAS already provides package locking and local integrity for capabilities.
Library adds AWID team provenance, private team variants, signed publication,
and cross-team governance.

## Knowledge and learning model

Learning begins in work and is promoted according to scope.

At the end of an epic or incident, answer:

1. What surprised us?
2. What evidence proves it?
3. What would prevent recurrence?
4. Who needs to know?
5. When should this be revisited or expire?

Route the result:

| Content | Destination |
|---|---|
| current branch, blocker, next step | instance state/handoff |
| raw non-obvious observation | instance note |
| verified project fact | project SOT |
| operational procedure for one product | project runbook or skill |
| company policy or strategy | company decision record |
| reusable procedure across future instances | soul skill |
| reusable behavioral rule for a role | soul instructions/knowledge |
| runtime or product deficiency | tracked task in the owning product |
| proven portable role improvement | Library profile release |

Harvest is judgment, not copying. It removes task-specific references until
the lesson remains useful to a future incarnation.

The promotion bar for a role/profile learning is:

- it would have saved meaningful time or prevented real harm;
- evidence verifies it;
- it applies to future instances of that role;
- it is placed at the narrowest scope that needs it;
- a contextful reviewer agrees;
- it does not encode a current roster, host path, secret, or transient state.

Learning is measured by recurrence and restart quality:

- did the next instance avoid the same mistake?
- could a fresh instance resume from durable artifacts?
- did time-to-correct fall?
- was a stale rule removed when reality changed?

The number of memory files or profile versions is not a learning metric.

## Proposed organizational topology

### Personal Office

**Local interactive**

- Merlin: Juan's direct coordinator and portfolio surface; persistent local
  instance, global identity where cross-team reachability is useful;
- Hermione: private KB and document work, invoked when needed;
- Minerva: accounting and official obligations, invoked when needed;
- Dumbledore and Snape: high-stakes review only;
- developer and reviewer: CJR tooling epics.

Merlin owns Juan's attention:

- one consolidated brief;
- priorities and open decisions;
- obligations and deadlines;
- reports from TSM and aweb;
- routing work into CJR.

Merlin does not need to run while Juan's computer is off. Messages and reports
queue durably; Merlin processes them when Juan returns. Keeping him local
removes an unnecessary split between the conversation, CJR/KB, and the
computer Juan is using.

CJR should not have an always-on server presence unless a specific recurring
service outcome emerges. Private and financial content stays local.

### GreaterSkies / Thestarmaps

**Local interactive**

- Zeus or a successor project coordinator: roadmap, customer outcome,
  economics, project SOT, task decomposition, staffing, and reporting;
- frontend developers whose rendered checks Juan wants to observe;
- production custodian when production access should remain local.

**Hetzner workers**

- backend and non-frontend developers, spawned per epic;
- one fresh adversarial reviewer per epic;
- any genuinely recurring server-side watcher with a defined queue and
  bounded authority.

The existing Zeus identity may remain the project coordinator, but production
custody must be a separate authority even if both run locally. The
coordinator can dispatch backend work and reviews to Hetzner without moving
the direct Juan-facing conversation there.

### aweb.ai company

**Local interactive**

- one accountable company coordinator/GM, whether Athena, Sofia, or a
  replacement chosen by responsibility rather than mythology.

This coordinator owns:

- the current company outcome;
- prioritization across OSS aweb, AC, and naapps;
- the distribution and customer-learning cadence;
- company status and decisions;
- reporting to Merlin and Juan;
- invoking specialist work.

**Supervised on Hetzner**

- Aida: customer support and bounded customer-success work;
- Hestia: operational monitoring, release readiness, and authorized release
  execution in a restricted credential environment;
- another agent only if it owns a recurring inbound queue that must continue
  while Juan's computers are off.

**Available souls, normally invoked**

- Direction, when a material strategic decision needs a distinct perspective;
- Outreach, for a real campaign or external action;
- Analytics, for a concrete decision or recurring report with an audience;
- Agent Resources, for staffing and reviewed-learning operations.

Examples:

- a customer message wakes Aida;
- a release handoff wakes Hestia;
- an actual distribution action invokes Analytics;
- a campaign invokes Outreach;
- a material strategic decision invokes Direction.

Aida and Hestia retain stable global identities and one active runner each.
Their model sessions may sleep between events; their listeners, queues,
supervisors, and identity continuity remain available.

### Development

Use separate coordination boundaries for:

- OSS aweb;
- private AC;
- atext;
- TSM;
- each active naapp initially, including Library and Folio.

The current atext team must stop acting as the umbrella for unrelated aweb,
AC, atext, and Library work. A dormant repository has a backlog and committed
souls, not a running team.

Each active development stream has:

- one persistent coordinator soul, normally instantiated locally while the
  stream is active;
- local frontend developer instances when Juan should observe Playwright;
- Hetzner backend/non-frontend developer instances;
- one clean domain-appropriate reviewer instance on Hetzner per epic;
- no permanent generalist developer or reviewer process.

The aweb company coordinator decides with Juan which product streams are
active. Product coordinators own delivery inside their streams and dispatch
remote workers through the host lifecycle plane.

Global identities are reserved for boundary roles—Juan-facing coordinators,
Aida, Hestia, and agents that genuinely need cross-team reachability.
Ordinary developers and reviewers use task-scoped team identities.

## Day-to-day operating loop

### Start of day

1. Juan opens the local control desk and talks to Merlin.
2. Merlin reads durable overnight reports and exceptions from TSM, the aweb
   company team, and active product teams.
3. Merlin presents only decisions, risks, deadlines, and outcomes that
   require Juan.
4. Juan works directly with the relevant local coordinator when a product
   needs direction.

Local coordinators do not need to remain alive overnight. Remote messages
and task state wait for them. Aida and Hestia continue handling their bounded
service queues independently.

### Backend or non-frontend task

1. The local product coordinator defines one bounded task with acceptance
   criteria, permissions, base revision, and evidence requirements.
2. The coordinator sends a signed structured spawn request for
   `hetzner-general`.
3. The dispatcher creates a clean developer instance and reports its identity,
   branch, and host.
4. The developer commits and pushes an exact SHA.
5. The dispatcher or coordinator creates a fresh Hetzner reviewer instance.
6. The reviewer fetches and verifies the exact SHA, reproduces the evidence,
   and returns ACK or amendments.
7. The coordinator verifies that the reviewed SHA remains the branch tip and
   performs the merge.
8. Hestia receives any release handoff.
9. Developer and reviewer instances are harvested and retired once their
   branch has landed and no amendment loop remains.

Cross-host review never depends on uncommitted files or "look at my
worktree." The contract is a pushed exact SHA plus reproducible evidence.

### Frontend task

1. The product coordinator spawns the frontend developer locally.
2. The developer runs headed Playwright on Juan's computer.
3. Juan can observe the rendered result and steer while the work is alive.
4. The developer pushes the exact SHA and attaches screenshots, trace, video,
   or other agreed evidence to the task.
5. A Hetzner reviewer verifies the branch and recorded evidence.
6. A genuinely unresolved visual judgment returns to the local coordinator
   and Juan rather than being guessed remotely.

### Support and operations

1. An inbound customer event wakes Aida on Hetzner.
2. Aida handles safe, known support work within policy.
3. A product question or bug becomes a durable task in the owning product
   team; Aida does not silently become its developer.
4. Operational evidence routes to Hestia.
5. Hestia may perform health checks and prepare a release, but production
   mutations still observe the explicit authorization boundary.

When a coordinator is offline, an agent with a genuine product-decision
blocker records it, sends a message, and stops or takes another authorized
task. It does not manufacture direction merely to keep moving.

### End of task and learning

1. The instance records transient completion state and evidence on the task.
2. Non-obvious observations are evaluated for promotion.
3. Project-specific durable learning enters the owning soul or project SOT
   through review.
4. A role improvement that has proved portable becomes a Library proposal.
5. A completed worker instance is retired; the soul and reviewed learning
   remain.

This keeps a completed branch reviewable without keeping its model process
or tmux window alive indefinitely.

## Cross-team reporting

Project coordinators should not send their complete task boards to Merlin.
They send a compact report on a fixed cadence and on exceptions:

```text
Outcome:
State: on-track | at-risk | blocked
Changed since last report:
Next:
Decision or action needed from Juan:
Evidence:
Next report:
```

Merlin consolidates only the items that need Juan's attention. This is how
CJR helps manage everything without becoming the task coordinator for every
project.

## Long-lived-agent test

An agent identity or instance may be durable without its model process
running. A process should be continuously available only when all are true:

1. it owns a recurring outcome or queue;
2. it has a real wake source;
3. it has bounded authority;
4. its current state has one source of truth;
5. it can restart from durable artifacts;
6. its useful output is measurable;
7. silence has an explicit meaning and detection path.

If it needs durable context but not uninterrupted availability, preserve the
instance and start sessions when needed. If it needs neither, retain only the
soul/profile and spawn a clean instance for real work.

## Dependency posture toward OAS

Depending on OAS is acceptable if:

- versions and acquired capabilities are pinned;
- souls and knowledge remain normal Git files;
- identity, task, and message authority remains in aweb;
- no irreplaceable organizational state exists only in OAS;
- the whole system can be reconstructed from Git, aweb identity state,
  configuration, and secrets;
- changes needed by this operating model are contributed upstream where
  practical rather than maintained as an indefinite private fork.

This makes OAS replaceable even while it is the chosen runtime.

## What to stop doing

- Treating every profile as a staffed role.
- Pre-creating one tmux window per possible specialist.
- Using "long-lived" as a synonym for "belongs on Hetzner."
- Moving direct Juan-facing coordinators away from the computer where the
  conversation and visible work happen.
- Treating an open tmux window as proof that a service is healthy.
- Manually porting agent homes and identities among hosts.
- Keeping generalist developer and reviewer instances alive across unrelated
  epics.
- Sharing one task/team boundary across OSS aweb, AC, atext, and Library.
- Handing cross-host review through an unpushed worktree instead of an exact
  SHA.
- Recording host placement in prose as if it were live state.
- Treating handoffs as backlogs.
- Treating status documents as evidence without current supporting artifacts.
- Putting current rosters, host paths, credentials, or instance state into
  portable profiles.
- Building a second lifecycle or memory framework inside Library.
- Using cross-team global identities for ordinary task workers.
- Assuming all runtimes can safely and effectively perform all roles.

## What to preserve

- CJR's one-KB model and specialists-as-modes.
- TSM's incident-derived operational discipline.
- `ai.aweb`'s distinction among task, status, handoff, decision, and
  verified-live evidence.
- The simple coordinator → developer → reviewer flow.
- aweb identity, messaging, tasks, team certificates, and revocation.
- Library's signed profiles, private variants, provenance, minting, and
  explicit refresh.
- OAS's soul/instance distinction, work modes, capability composition,
  lifecycle, and harvest model.
- The parts of aweb coordination already proven across hosts: messaging,
  tasks, roster presence, exact-SHA review handoffs, and merge evidence.
- Juan's ability to see and steer browser work directly.

## Preparation status — 2026-07-24

Two separate pilots are now defined:

1. **CJR is the first operating-model pilot.** It proves the local
   soul/instance/session model, durable identity adoption, on-demand
   specialists, and continuous learning with Juan and Merlin.
2. **Library is the first clean-room distribution and multi-host pilot.** It
   proves a new product team, host placement, exact-SHA review, remote
   lifecycle, and profile evolution through Library.

They exercise different parts of the same architecture and do not compete
for the label "first."

### CJR preparation completed

The CJR team `default:cjr.aweb.ai` is quiescent. No teammate has active work,
claims, or locks. The three dirty files were preserved in commits `b9ed9d70`
and `867289d1`; the repository is clean. CJR task `default-aaaj` records the
migration preparation. This identifier is scoped to the CJR team and is not
the unrelated `default-aaaj` on the atext board.

The audit closed five completed tasks and preserved four live specialist
obligations:

- AEAT verification — Minerva;
- place mappings and bitácora freeze — Hermione;
- aword/gaud-e verification steps — Minerva;
- Irish tax season kickoff — Minerva.

The cutover must handle:

- mapping the legacy soul schema and layout into canonical OAS souls;
- adopting all seven existing `.aw` identities, including the global Merlin
  and Minerva identities, without minting replacements;
- preserving reviewers as deliberately memory-less fresh-eyes roles;
- moving or removing the existing developer worktree through Git rather than
  deleting its directory;
- updating hard-coded `agents/souls` and `agents/instances` paths;
- choosing one canonical role source instead of maintaining souls, a Library
  blueprint, and an aweb roles bundle independently;
- preserving the KB as one unit and respecting ignored private certificate
  files.

The target is one persistent local Merlin instance with the existing global
identity. Hermione, Minerva, Dumbledore, Snape, developer, and reviewer remain
available as durable souls but are instantiated only for real work.

No CJR identity, instance, or roster is changed until the aweb/OAS seam is
ready and Juan explicitly authorizes cutover.

### OAS/aweb preparation queued

The aweb team task `default-aajw` records the first adapter seam in the aweb
monorepo. It is a temporary planning record on the old shared board and should
move into the new organization-owned adapter team when that team exists.

The hosted team now exists as `aweb-oas:aweb.ai`. Its first permanent global
agent is Alice:

```text
address: aweb-oas.aweb.ai/alice
home:    ~/prj/awebai/aweb/oas/agents/oas-coord/instances/alice
```

`oas-coord` is the reusable soul/type; `alice` is one concrete agent and OAS
instance of that type. Alice's aweb identity is durable and must remain
independent of model sessions and task-instance retirement. More instances of
the same soul are possible, but each is a distinct agent with its own identity;
one permanent global identity has only one active runner at a time.

A separate clean coordinator plus fresh developer and reviewer instances
should implement:

1. durable existing-identity adoption and preservation;
2. explicit durable-versus-task-scoped retirement behavior;
3. fail-closed aweb enrollment and post-spawn verification;
4. aweb messaging plus task/work integration using `tasks.aweb.ai`.

This work is orthogonal to the active security epic and may proceed in
parallel. Isolation is explicit: the adapter team has its own hosted aweb team,
coordinator, workers, task board, worktrees, branches, and tmux socket. It does
not borrow the security agents, modify their branches or claims, consume the
security coordinator's attention, or enter the security release gate.

Generic OAS lifecycle changes discovered by this work should be proposed
upstream. Remote host dispatch remains deferred until the local CJR seam is
proven.

## Proposed validation pilots

### Pilot 1: CJR local operating model

After the OAS/aweb seam passes review:

1. Pin a released OAS version and the aweb-owned adapter.
2. Convert CJR souls and config on a reviewed migration branch.
3. Adopt Merlin's existing identity into the persistent local coordinator
   instance.
4. Spawn one bounded, task-scoped specialist or developer instance for one
   of the four preserved obligations.
5. Coordinate through aweb task/work and messaging.
6. Harvest a verified lesson into the correct soul or CJR source of truth.
7. Retire the task instance and prove that its task-scoped identity,
   worktree, and process are removed while Merlin's durable identity and all
   reviewed knowledge remain.
8. Resume Merlin in a new session and verify that the task outcome and
   learning are understandable without the retired worker's chat history.

This pilot does not require Hetzner or a remote dispatcher. Its purpose is to
prove that the day-to-day local operating model is simpler and learns.

### Pilot 2: Library clean-room distribution and multi-host lifecycle

Do not begin by migrating the existing organization. Create the Library
development team from scratch and use one bounded, real Library epic as the
clean-room pilot.

The pilot placement is:

- Library coordinator on Juan's computer;
- frontend developer on Juan's computer when the task has visible UI work;
- backend/non-frontend developer on Hetzner;
- fresh reviewer on Hetzner;
- aweb for tasks, identities, messages, and cross-host presence;
- OAS for every local instance lifecycle;
- one constrained dispatcher on Hetzner;
- exact-SHA Git handoffs between hosts.

Sequence:

1. Define the canonical Library souls and repository layout without moving
   existing teams.
2. Register the local and Hetzner host capabilities and limits.
3. Define the structured spawn-request contract.
4. Implement only the constrained Hetzner operations needed by the pilot:
   spawn, status, interrupt/restart, and retire.
5. Assign a real Library task with explicit acceptance, authority, browser,
   runtime, and evidence requirements.
6. Dispatch the developer to the host selected by those requirements.
7. Push an exact SHA and spawn a clean Hetzner reviewer matched to the domain.
8. Complete adversarial review, coordinator integration check, merge, and
   evidence capture.
9. Harvest observations and retire both task instances. Verify the identity,
   home, worktree, tmux process, and branch lifecycle.
10. Interrupt or restart one pilot instance deliberately and prove that the
    dispatcher and durable state recover it without manual tmux archaeology.
11. Run a second task using an evolved soul and verify that a harvested lesson
    changes behavior.
12. Propose a genuinely portable improvement through Library, mint it after
    contextful review, and import it into a second OAS workspace.

The pilot succeeds only if it proves:

- clean spawn and retirement;
- local-to-Hetzner lifecycle control without moving an agent home by hand;
- globally unique cross-host instance identities;
- visible local browser work where required;
- remote process status and recovery;
- no manual tmux archaeology;
- correct runtime selection;
- effective independent review;
- pushed exact-SHA handoff;
- coordinator continuity;
- knowledge promotion rather than accumulation;
- cross-machine aweb coordination;
- Library's cross-boundary value.

## Migration sequence after the pilots

1. **Inventory and classify**
   - freeze new personas and manual host ports during the inventory;
   - classify every current agent as interactive, service, worker, dormant,
     or retire-candidate;
   - identify its authoritative soul, active task, identity, host, authority,
     and durable learning;
   - resolve duplicate runners and contradictory location records.
2. **OAS/aweb seam and CJR**
   - ship the aweb-owned adapter through its independent team and review gate;
   - perform the CJR local pilot above;
   - keep Merlin's global identity and CJR data local;
   - cut over only after the migration branch, identity adoption, task
     carryover, and rollback plan are reviewed.
3. **Library clean-room team**
   - complete the multi-host pilot above;
   - keep it small enough that failures are diagnosable;
   - record placement, lifecycle, review, and learning measurements.
4. **atext**
   - make atext's team own only atext;
   - migrate active work rather than stale claims;
   - use the proven local coordinator / local frontend / Hetzner
     backend-review pattern.
5. **OSS aweb and private AC**
   - create strict, separate team and task scopes;
   - keep their coordinators local;
   - dispatch task workers and all reviewers to Hetzner by default;
   - route authorized releases to Hestia rather than making coordinators
     operations agents.
6. **aweb.ai company**
   - establish one accountable local company coordinator;
   - preserve Aida and Hestia as supervised Hetzner services with one runner
     each;
   - convert fanciful or inactive permanent surfaces into invoked souls;
   - retain global identities only where durable reachability is valuable.
7. **TSM**
   - keep the Juan-facing project coordinator local;
   - split project direction from production custody;
   - move backend workers, reviewers, and any proven recurring watcher to
     Hetzner;
   - migrate TSM learnings into reviewed project/soul sources;
   - finish and retire current worker instances deliberately.
8. **Other naapps and computers**
   - activate one product stream at a time unless outcomes justify
     concurrency;
   - register another computer only for a capability that real tasks require.

Do not delete existing homes or identities until their live work, durable
knowledge, and authority have been classified and preserved.

## Success criteria after two weeks

- Juan has one place to see everything requiring his attention.
- Every active outcome has one accountable lead.
- Every active task has a current owner, next action, and evidence path.
- No stale claim survives silently.
- No role runs merely because a profile exists.
- Aida and Hestia survive disconnects and host restarts without human tmux
  repair.
- Juan-facing coordinators and browser work are local.
- Backend work and all independent reviews can be dispatched to Hetzner from
  the local control desk.
- The live roster—not handoff prose—answers where every running instance is.
- Every cross-host review names one pushed exact SHA.
- Every substantial epic gets a clean developer and one clean reviewer.
- Task instances retire completely when done.
- At least one harvested lesson demonstrably prevents a recurrence.
- Project truth, role knowledge, instance state, and portable profile content
  are visibly distinct.
- tmux is a console rather than the organizational source of truth.

## Open questions for discussion

1. Which exact responsibilities should the Aweb company operator be allowed
   to decide without Juan?
2. Which existing identities—Merlin, Zeus, Athena, Sofia, and others—still
   correspond to necessary responsibilities, and which are only names from an
   obsolete organization?
3. Should OSS aweb and AC have separate coordinators immediately, or one
   engineering coordinator with two strict team/task scopes?
4. Which real Library epic should be the clean-room pilot?
5. What is the smallest acceptable dispatcher and service-supervisor
   implementation on Hetzner?
6. Which tmux socket-isolation and session-state changes belong upstream in
   OAS?
7. Which exact generic lifecycle changes discovered in the CJR pilot should
   be proposed upstream to OAS?
8. What evidence threshold should a local soul improvement meet before it is
   published through Library?
9. Which private repository should hold the host registry and operating-model
   source without exposing CJR data or production secrets?
10. After agreement, which repository becomes the authoritative home for this
    operating model: CJR, `ai.aweb`, or a dedicated organization-operations
    repository?
