---
name: verify-main-worktree-before-merge
description: Before a coordinator merge, confirm the main worktree's HEAD is actually on `main` — it can drift onto a review branch and silently no-op the merge.
metadata:
  type: project
---

When merging a branch into folio/atext main from the coordinator's main
checkout, the worktree's HEAD can be sitting on a stray branch (e.g.
`review-<branch>` left over from a review checkout) rather than `main`.
Observed cause: reviewer-2 validated folio branches by checking them out
*inside* the shared `/Users/juanre/prj/awebai/folio` working copy (creating
`review-<branch>`), instead of in a detached worktree like reviewer does.
That left the coordinator's checkout on the review branch. Fixed by asking
reviewer-2 to use `git worktree add` for reviews — but always defend with
the check below regardless of cause. If
you run `git merge --no-ff origin/<branch>` while HEAD is already AT that
branch's tip, git reports **"Already up to date"** and the subsequent
`git push origin main` says **"Everything up-to-date"** — so it LOOKS
merged but nothing happened and main never moved.

Always, before merging:

```
git rev-parse HEAD; git branch --show-current      # must be on main
git merge-base --is-ancestor origin/<branch> main  # expect NO before merge
```

After merge, confirm `git ls-remote origin main` == local `main` AND that
main's hash actually advanced. If the worktree drifted, `git checkout main`
first (verify clean tree), merge, push, then delete the stray branch.
See [[instance-worktrees-need-explicit-push]].
