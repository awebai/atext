# Restart handoff: OAS–aweb code and strategy review

Date: 2026-07-27

## User objective

Evaluate the current OAS–aweb implementation against Pepe's desired customer
experience and the proposed agent-team operating model, then choose the best
path forward.

## Verdict already delivered

The identity lifecycle code is a strong source-level prototype, but it does not
yet deliver a clean customer journey.

The next milestones are:

1. one canonical, installable, aweb-owned OAS package;
2. a clean ordinary-worker journey from `oas install` through message/task and
   residue-free retirement;
3. a resident journey proving the same durable principal and reviewed learning
   survive session replacement;
4. remote dispatch and Library integration only after those two journeys work.

Do not build Library as a workaround for incomplete spawning, identity,
messaging, or learning. Library remains the governed profile/knowledge
distribution layer, reached through an adapter.

## Pepe's desired experience

- An engineer installs the organization's OAS config at the workspace root.
- `oas install` acquires capabilities and CLIs and guides the engineer into the
  configured aweb team.
- All OAS instances in that workspace join the team under the engineer's
  sponsorship/name.
- Repository configs can override workspace defaults.
- aweb tasks may be the default task layer; Linux can override it with Jira.
- Parent/sibling relationships appear in the OAS panel.
- Knowledge and Library capabilities can be added without conflating their
  responsibilities.

## What currently works

- OAS configuration cascades and repository/soul/type overrides exist.
- Locked capability acquisition and consented CLI installation exist.
- Current OAS source contains parent/sibling relationships and panel support.
- Local disposable aweb identity provisioning has journaling, reconciliation,
  cleanup, and `AWEB_IDENTITY_HOME` propagation.
- Messaging and tasks are correctly modeled as separate exclusive layers.
- Canonical source-to-source tests passed: `make test-oas`, 83/83.
- Targeted `aw` identity-home/local-provisioning Go tests passed.

## Blocking gaps

1. The default ordinary-worker path requires a local team controller. Hosted
   provisioning is refused, so a normal invited organization member cannot use
   the mainstream flow.
2. `aweb.identity-attach` claims the messaging layer but includes no messaging
   skills, channel setup, roster commands, or plugin integration.
3. OAS spawn-hook failure remains advisory, so an unbound instance can still be
   created. Identity/team preflight must fail closed.
4. The current alias is `oas-<opaque hash>`, not a readable sponsored identity.
   Sponsor, deployment, OAS instance, and parent lineage are not structured
   aweb metadata.
5. Durable provisioning is rejected. `attach-existing` is only partial.
6. Principal selection is soul/type-scoped, not per-instance.
7. The principal declaration path hardcodes `oas/agents` below the context. In
   the current `aweb/oas` layout it resolves through `aweb/oas/oas/agents`, so
   Alice's actual home is not found.
8. The deployment `oas-config.yaml` is untracked and selects neither tasks nor
   knowledge. Alice's current home has no OAS instance declaration.
9. There are two competing messaging capabilities: the new aweb-owned adapter
   has the stronger lifecycle substrate, while upstream `oas.aweb` has more of
   the actual messaging UX but weaker lifecycle behavior.
10. The integration passes against an OAS source checkout, not the installed
    release. The installed OAS is 0.18.0; the source contract includes upstream
    changes that remain under review. Installed `aw` was 1.33.0 while local
    source/tag is 1.34.0.

## Recommended customer contract

Keep acquisition and remote onboarding architecturally distinct while allowing
one guided UX:

```text
oas install
  -> install locked capabilities and compatible CLIs
  -> show requested aweb team/scope
  -> ask for consent
  -> perform setup, or report exactly one setup action
```

Do not add arbitrary server restrictions solely because OAS is the caller.
Use existing scoped/expiring invitations. The missing hosted contract is that a
sponsor or narrow service can create and fully retire only the workers it owns,
without putting a team-owner credential in a model-readable filesystem.

## Golden acceptance journeys

### Ordinary worker

```text
clone organization workspace
-> oas install
-> accept one team/setup action
-> spawn developer
-> readable aweb address appears in OAS status
-> exchange a real message
-> receive/complete a task
-> parent/sibling relation appears
-> retire
-> no live identity, certificate, membership, or workspace residue
```

### Resident

```text
select existing Alice or Merlin principal per instance
-> start through OAS
-> receive and answer a message
-> stop and replace the session/instance
-> restart with the same principal
-> retain reviewed local/Git knowledge
-> publish to Library only through explicit review
```

Use `attach-existing` to prove the resident path before implementing durable
principal creation.

## Primary references

- `artifacts/agent-team-operating-model-proposal.md`
- `~/prj/awebai/aweb/oas/docs/oas-aweb-seam.md`
- `~/prj/awebai/aweb/oas/.agents/capabilities/owned/aweb-identity-attach/`
- `~/prj/awebai/aweb/oas/.agents/capabilities/owned/aweb-tasks/`
- `~/prj/awebai/oas/capabilities/oas-aweb/`
- Alice: `aweb-oas.aweb.ai/alice`
- Alice mail conversation: `5c25957f-2c8b-4810-b888-c5a02de1614c`

## Local state to preserve

- Developer soul has an uncommitted review-memory addition:
  `work/agents/souls/developer/memory/cross-product-integration-reviews.md`
  and its `MEMORY.md` index entry.
- `work/uv.lock` was pre-existing and untracked; do not modify or claim it.
- No product code was changed during the review.

## Security follow-up

Alice's stored aweb API credential appeared in diagnostic command output during
the review. Do not copy it into any handoff. Rotate it after restart.
