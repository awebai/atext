# tmux dogfooding isolation

Never run `tmux kill-server` or `tmux kill-session` against the default socket. One unguarded kill-server on the default socket kills every live agent session across teams.

For any dogfooding/testing that launches tmux (`aw team up`, `aw team add --start`, or plain `tmux`):

1. Set `TMUX_TMPDIR` to a fresh `mktemp -d` directory before launching anything.
2. Use only named throwaway sessions on that isolated socket.
3. Clean up only those named throwaway sessions, never the whole server.
4. Verify nothing leaked to the default tmux server/socket.

Window/pane-level commands for legitimate operations remain fine.
