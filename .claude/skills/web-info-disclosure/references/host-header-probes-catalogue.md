# Host and forwarded-header probing — case catalogue

The app's trust in Host/X-Forwarded-Host splits internal vs external views — some artifacts only serve to the internal name.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | Host: internal-name returns different content | vhost routing | the internal vhost |
| 2 | X-Forwarded-Host: localhost flips a 403 | host allowlist | read the restricted path |
| 3 | Server: header changes with Host | multi-vhost | enumerate names |

## Falsifier

Falsifier — every Host variant returns the same content: single vhost, nothing hidden behind routing.
