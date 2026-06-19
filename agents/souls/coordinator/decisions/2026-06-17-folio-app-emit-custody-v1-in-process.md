# folio app-emit custody (v1): in-process signing with a platform-managed app service key

Date: 2026-06-17
Status: SUPERSEDED 2026-06-18 by SELF-CUSTODY (SoT 6.7 amended, aweb commit
6d63c9ea). In-process signing is RETAINED; the *platform-managed key* part is
gone. See the "2026-06-18 self-custody amendment" section at the bottom.

Original status: ADOPTED — Juan nodded 2026-06-17 ("yes go ahead"). v1 =
in-process signing with a platform-managed (hosted) / own (self-hosted) app
SERVICE key. (aweb-coordinator + consultant confirmed the model.)

## Question

Juan asked, from first principles, why folio has a Python emit-credential signer
(`aaag.11`, `src/folio/app_emit.py`) — and whether a *hosted* app should hold its
own emit-signing key, given `trust-model.md` says hosted/deployment-held keys are
**custodial** (operator holds the encrypted key).

## The resolving distinction

Two things were (reasonably) fused and must be separated:
- **Custody classification** — who holds the key, on whose behalf.
- **Signing location** — where the bytes actually get signed.

"Custodial" does NOT force "a gateway signs." The platform can store folio's
encrypted emit key and **provision it into folio's hosted runtime**, which signs
**in-process**. Custodial-classification + in-process-signing coexist.

And the deeper correction: the hosted=custodial vault exists to protect
**user/agent identity keys** (so people needn't hold keys). folio's emit key is a
**service credential of folio-the-principal** — no third-party user to protect —
so an app legitimately holds its own service signing key, hosted or self-hosted.
That's deployment-secret management, not the user-identity custodial vault.

## Lock (v1)

> Hosted first-party app emit keys are platform-managed app SERVICE credentials.
> The platform stores them encrypted and provisions them to the hosted app
> runtime for IN-PROCESS signing of app-event credentials. Distinct from
> user/agent custodial identity. Core verifies the emitted credential against the
> installed app's active kid/did_key + app/team grant. A central gateway/KMS
> signer is FUTURE hardening (fits aaaj.6 app-as-AWID-identity), not v1.

## Consequences

- **Keep `aaag.11`.** The Python signer is the real v1 emit primitive — used by
  self-hosted folio (own `.aw` key) AND hosted folio (platform-provisioned
  encrypted key). It is NOT misplaced.
- folio still **emits nothing today**; the emit path (e.g. `asset.video.status`
  ready, `present.edited`) is forward-looking. The signer is the primitive that
  path will use.

## Guardrails for the eventual emit implementation (not built yet)

1. NEVER reuse an agent identity / team-controller / namespace-controller /
   A2A-gateway key as an app emit key — **per-app/per-env/per-kid only**.
2. The VERIFIER is the authority, not the app's self-claim: bind
   `app_id + team_id + kid + did_key` to an installed/granted record; reject
   inactive/rotated keys. (m3.2 already enforces this via digest-scoping.)

## Open future call

Strict **gateway/KMS-signed** custody (folio never holds the raw key; smaller
blast radius) is real future hardening, tied to `aaaj.6`. If adopted, the
in-process signer becomes the self-hosted/conformance reference rather than the
hosted path — but it stays either way. See the manifest/dispatch work
([[2026-06-16-folio-aw-verbs-via-manifest-not-binary]]).

## 2026-06-18 self-custody amendment (the real model)

Juan interrogated the platform-managed model with two questions — "could the
key be held by your own server?" and "doesn't this let any app join without
deploying keys in AC?" — and they dissolved the whole apparatus. SoT 6.7 was
amended to **self-custodial** (aweb commit `6d63c9ea`):

- The app (folio, any anapp) **generates and holds its own emit seed** in its
  own runtime, like any other app secret. It declares only the **public**
  `did_key` in its manifest `event_emitters`.
- The platform **registers the public key + grant at install** — never mints,
  holds, or provisions a private seed.
- This **deleted** the entire seed-injection apparatus we'd designed (Option C
  encrypt-to-ops, GPG keypair, scoped Render token) — none of it was needed.
- Wire + verifier unchanged (byte-parity vectors unaffected); rotation = app
  regenerates + re-registers. **Any app joins without deploying keys in AC** —
  AC holds only public keys + grants, smaller blast radius. The ecosystem model.

folio implemented it: operations self-generated folio's keypair (seed in a 0600
ops file → Render env), developer-frontend declared the public key in the
manifest (digest `480b1577`), AC registered the public key straight from the
manifest. folio's deployed instance auto-emits on append, signing with its own
seed.

## The lesson the proof taught (verified ≠ components green)

The live folio emit→wake proof — which Juan insisted on running end-to-end —
found a bug invisible to every green test: the **AC cloud middleware**
(`aweb_cloud/middleware/auth_bridge.py`) intercepts `/api/v1/events/app`, only
recognizes the bare `DIDKey` scheme, and **401s the emit before it reaches the
(correct) app-event verifier**. Signer-conformance tested the signer; verifier
tests tested the verifier; nothing exercised the cloud middleware between them —
so m3.2's app-event emit had never worked through the live `/api` layer, yet was
declared "live + verified."

**"Verified" must mean the end-to-end capability demonstrated, not the
components individually green.** And a feature isn't shippable until its
*consumer* surfaces ship: app-event support sat unreleased on `main`
(`channel-core` 45d414d2) while `claude-channel` 1.4.12 / `pi` 0.1.21 — the
packages in live agent sessions — predated it, so no agent could be woken.
Insisting on the real end-to-end test (an actual agent roused by the event) is
what surfaced both gaps. See [[browser-features-verify-against-running-instance]].
