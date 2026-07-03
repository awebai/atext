# Push your handoff branch to the remote before saying it is ready to merge

A local commit the coordinator cannot see is not a handoff. On default-aafr I
committed to default-aafr-ia and sent the handoff with the sha, but never ran
git push — the coordinator's git ls-remote showed no such branch and they could
not merge.

**Why:** I had skipped the push out of habit — on the prior task another
developer folded my branch into the shared review branch and pushed it, so my
commit reached the remote without my pushing. That is the exception, not the
rule: when I hand a branch off for merge, the branch is mine to publish.

**How to apply:** before a handoff mail/chat that names a branch + sha for
merge, run `git push -u origin <branch>` and verify with
`git ls-remote origin <branch>` that the remote sha matches, then say it is
ready. Related: [[verify the push landed before announcing a merge]].
