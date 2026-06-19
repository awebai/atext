# Library profiles: public/private visibility + continuous team improvement

Date: 2026-06-19
Status: ADOPTED — Juan, 2026-06-19 ("profiles should be public or private...
teams can create new profiles, private by default but can be made public for
other people to use. ... a crucial aspect of what we are doing is to enable
agent teams to improve, so teams will be continuously updating their profiles").

## Requirement

1. Profiles (and packs as the shareable unit) carry **visibility: public |
   private**, **private by default**.
2. Teams can **author new profiles**, owned by the team.
3. A team can **make a profile public** for other teams to use — a cert-auth
   state transition performed by the owning team.
4. **Continuous improvement is the point.** Teams update their profiles
   constantly; the learning-proposal workflow (.14.6) is the core engine, not a
   nice-to-have.

## The crux: visibility ≠ content (do not digest it)

Profile identity is `(id, version, digest)`, digest = sha256 of the canonical
JSON of the profile **content** (the conformance-vector'd primitive shared with
the aw CLI lane — see [[2026-06-17-folio-app-emit-custody-v1-in-process]] for the
byte-parity pattern we're reusing).

- **Visibility and `owner_team` are mutable access-control attributes stored
  ALONGSIDE the versioned content — NOT part of the canonical/digested form.**
  Flipping private→public changes WHO can fetch a content, not WHAT it is, so the
  digest must be identical before/after. Folding visibility into the digest would
  (a) break content-addressing, (b) perturb the Go/Python conformance vector,
  (c) desync aw's cached `.aw` ref/snapshot on a pure visibility flip.
- **Improvement = new content version = new digest.** Versioning (content) and
  visibility (access) are orthogonal axes.
- Adopting another team's public profile and improving it = a **team-private
  variant** (fork) the adopting team owns. Already in the SOT ("team-private
  variant").

## Ripple to the tasks

- **.14.2 (model):** profile + pack gain `visibility` (default private) and
  `owner_team`; team-authored create flow; versioning as the central lifecycle.
  visibility/owner_team are columns/attributes, not digested fields.
- **.14.3 (catalog + cert API):** public catalog reads (`GET /v1/profile-packs`,
  `/v1/profiles/{id}`, unauth) return **public only**; team-cert reads return the
  caller team's private profiles + public ones. New cert-auth endpoints: create
  profile, update (new version), set visibility (make-public/make-private).
- **.14.6 (learning):** reinforce continuous improvement — proposals → approved →
  new content version or team-private variant; teams iterate their own profiles
  continuously; aw `.aw` homes refresh when the team chooses.

## Contract impact (aw lane)

The conformance-vector'd digest is **unaffected** (visibility isn't in it).
New dimension for aw: catalog reads split **public (unauth)** vs **private
(team-cert)**; materializing a private profile requires team-cert. Folded into
the .2.9-anchored signed draft.

## Tags (2026-06-19) — same pattern as visibility

Juan: profiles need user-applied TAGS (e.g. twitter, github, coder, marketing)
and the catalog must LIST/FILTER by tag — surfaced while organizing profiles.

Tags follow the visibility rule exactly: **mutable organizational record
metadata, NOT content — excluded from the digest.** Adding/removing a tag must
not change the profile version or digest (same as a visibility flip), so the
JUST-FROZEN byte-parity contract is UNAFFECTED — tags are never in the hashed
payload.

- **Model (.14.2):** profiles gain `tags` (list of normalized strings:
  lowercase, trimmed), a mutable owner-set record column. Packs may gain tags
  too; profiles are the requirement. Author-declared tags that live in the pack
  SOURCE (profile.yaml) are already file content and thus already in the digest —
  no special handling; the new thing is the mutable post-hoc tag column.
- **Catalog (.14.3):** list/filter by tag — `GET /v1/profiles?tags=...` and
  `/v1/profile-packs?tags=...`; public filters public, team-cert adds the team's
  private. New cert endpoint to set/add/remove tags on an owned profile.
- **v0 scope:** owner-set tags on the profile record; free-form strings, no
  controlled vocabulary; per-adopter tag overlays are a future nicety (YAGNI).
- **aw/contract:** frozen digest unaffected; only a new catalog FILTER dimension.
  No re-freeze.
