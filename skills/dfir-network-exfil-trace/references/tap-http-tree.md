# Taps: http,tree / http_req,tree / http_srv,tree

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What they answer

- `http,tree` — status codes and request-method counts.
- `http_req,tree` — requested URIs and per-host request counts.
- `http_srv,tree` — responses grouped by server.

## Command

```bash
tshark -r capture.pcapng -q -z http,tree -z http_req,tree -z http_srv,tree
```

## Reading for exfiltration

HTTP exfil usually rides POST. `http,tree` method counts (POST vs GET share),
then `http_req,tree` for which URIs received POSTs and which host. Upload
volume still comes from `conv,tcp`/`endpoints,ip` — the HTTP taps name the
endpoint, not the bytes.

## Evidence rule

A POST count plus a URI is the quotable answer to "which endpoint received
the upload". Quote the exact leaf, not the whole tree.

## Trap

HTTPS never reaches these taps. If `io,phs` shows `tls` and no `http`, the
HTTP story needs the keylog (`-o tls.keylog_file:`) or the host-side
artifacts — SNI alone is `fld-tls-sni` territory and is a client claim.

## Pivot

POST-heavy single URI -> `chan-http-post-*`; nothing but TLS -> `chan-tls-*`.
