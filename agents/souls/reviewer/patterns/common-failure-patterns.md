# Common failure patterns

Generalized recurring-issue categories only — never verdicts or memory about
a specific change. This is the reviewer's single persisted artifact; fresh
eyes are the point.

## Shared checkout disturbance during review

Do not check out review branches inside a coordinator or shared main working
copy. Review validation should happen in a throwaway worktree, for example
`git worktree add /tmp/<repo>-review-<branch> <branch>`, then remove it when
done. Leaving a shared checkout on a review branch can make another teammate's
merge/rebase/status operations silently operate on the wrong branch.

## Ambiguous review verdicts

A review response should go to the requester over chat and start with a clear
verdict: **ACK** with the exact evidence checked, or **amendments** with
`file:line`, why it matters, and a concrete fix. Verify before flagging, drop
pre-existing issues and CI-only nits, distinguish blocking findings from
follow-ups, and route product/authority calls to the coordinator instead of
turning them into code-review verdicts.

## Tmux default-socket nukes

Never run or approve dogfood/test cleanup that uses `tmux kill-server` or
`tmux kill-session` against the default socket. Those commands are socket-wide
and can kill unrelated live agent sessions. Any test that launches tmux must use
a fresh isolated `TMUX_TMPDIR`, operate only on named throwaway sessions in that
isolated socket, and verify nothing leaked to the default server; pane/window
commands for known scratch resources are the safe granularity.

## Published command lines as claims

In docs, skills, landing pages, and other published copy, every command line is
a product claim. For command-heavy reviews, verify each line against its own
authoritative surface rather than only the command named in the task: core verbs
against `--help`, plugin-dispatched verbs against the manifest/input schema and
dispatch rules. Require required params, reject unsupported bare positionals,
and ask for a line-by-line command handoff when the copy has many commands.

## Tmux default-socket destructive cleanup

Never use `tmux kill-server` or default-socket `tmux kill-session` in review or
dogfood validation. The default tmux socket may host live agent sessions for many
teams, so server/session cleanup can become a team-wide outage. Any test that
launches tmux (`aw team up`, `aw team add --start`, or plain tmux) must isolate
first with a fresh `TMUX_TMPDIR`, use named throwaway sessions, clean up only on
that proven-isolated socket, and verify nothing leaked to the default server.
Window/pane-level operations for your own scratch session are the safe boundary.

## Published command-copy verification

In published docs, skills, and landing-copy reviews, every command line is a
contract claim, not just the headline command named in the review request. Verify
each line against its own authoritative surface: core CLI verbs against `--help`,
plugin-dispatched verbs against the manifest/input schema and dispatch rules.
For plugin verbs, check that all required params are present and that the copy
uses flags rather than unsupported bare positionals. Ask for a line-by-line
handoff of command lines and required params when the change is command-heavy.
