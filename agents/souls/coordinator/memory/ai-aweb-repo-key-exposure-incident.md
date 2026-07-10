# ai.aweb workspace-key exposure (2026-07-10)

github.com/awebai/ai.aweb was PUBLIC while carrying the fused-soul agent
homes. The design intent held for signing keys — every `.aw/signing.key`
is a git symlink (mode 120000) into `co.aweb/keys/` (private repo), so no
signing-key material was ever exposed and no identity re-mint was needed.

What WAS exposed: `agents/<name>/.aw/workspace.yaml` committed as a
regular blob for hestia, athena, sofia, aida — each with a live 70-char
`aw_sk...` workspace API key to app.aweb.ai (transport auth: read team
mail/chat/tasks, post as the workspace; posts would be unverified without
the signing key). Also exposed, non-credential: interaction logs and
sofia's `.aw/drafts/` (internal correspondence).

Resolution: Juan flipped the repo private 2026-07-10 (verified
isPrivate=true). Rotation of the four workspace keys recommended but not
yet done — prior clones keep the history. `canonical_origin` in
identity.yaml points at the now-private repo; anonymous resolution 404s.

Lessons:
- "Private repo" is a claim to VERIFY (`gh repo view --json isPrivate`),
  never assume from content sensitivity.
- Symlinked-key layouts protect exactly what is symlinked; audit the
  sibling files (`workspace.yaml` held the live credential).
- Check git MODES before declaring key material exposed — a 120000 blob
  is a path string, not the secret.
- Before committing hestia's cutover churn: gitignore `.aw/workspace.yaml`
  (or `.aw/` wholesale), `secrets/`, and `dot-aw-bu.tgz`.
