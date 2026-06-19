---
name: post-reboot-ssh-agent-empty
description: After a Mac reboot the ssh-agent is empty; folio/atext pushes fail with publickey denied until the key is reloaded.
metadata:
  type: project
---

After a reboot of `altair.local`, the launchd ssh-agent comes up with no
identities loaded. Every push to a GitHub SSH remote (folio =
`git@github.com:awebai/folio.git`, atext likewise) fails with
`Permission denied (publickey)`. Developers may misread this as "my branch
is gone" and fall back to `gh` HTTPS, which silently queries the **atext**
repo instead of **folio** — folio and atext are separate repos, so they see
the wrong branch list and report the branch missing.

Fix (run from any shell in the shared login session; the launchd agent is
shared so one reload covers all local instances):

```
ssh-add --apple-load-keychain      # loads id_rsa from the macOS keychain
ssh -T git@github.com              # expect "Hi juanre! ..."
```

The GitHub key is `~/.ssh/id_rsa` per `~/.ssh/config`. Branch work is never
lost — verify with `git ls-remote origin <branch>` from the correct repo
before assuming anything is gone. See [[instance-worktrees-need-explicit-push]].
