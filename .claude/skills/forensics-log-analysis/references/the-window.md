# Reconstructing the sequence — the context window

One line rarely proves intent — the line before carries the
referer/prior request. `log_summary.py window access.log --around N`
or grep -n + sed -n 'N-20,N+20p' reads the surrounding session.

## What the window gives

- The requests that led to the hit (the path walked).
- The referer or prior request (the source).
- The response status/size (whether it worked).
- For auth.log: the Failed lines before the Accepted.
