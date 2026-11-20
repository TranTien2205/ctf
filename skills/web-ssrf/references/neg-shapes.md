# Negative shapes - what a dead SSRF looks like

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

- the parameter never reaches a fetcher: identical response for
  http://, file:// and garbage values - the input is a string
  field, not a URL; recorded verbatim.
- the fetcher resolves but the response is never returned: blind
  SSRF at most - a callback hit proves fetch, not exfil; graded
  blind, not read.
- the allowlist holds under every bypass tried (scheme case,
  userinfo, decimal IP, redirects): each refused variant is a
  negative line with its exact payload.
- the fetcher only proxies a fixed upstream: the URL is a
  template variable, not a fetch target - the parameter decides
  nothing about the destination.

## Ledger lines

'N schemes refused verbatim', 'callback received, no response
channel', 'allowlist held on M variants' - the counted negatives
are the falsifier evidence.

## Pivot

All fetch surfaces dead -> web-open-redirect (client follows) or
file-read-primitives (no fetch at all).
