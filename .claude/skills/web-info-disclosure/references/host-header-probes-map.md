# Host and forwarded-header probing — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Host: internal-name returns different content | vhost routing | the internal vhost |
| X-Forwarded-Host: localhost flips a 403 | host allowlist | read the restricted path |
| Server: header changes with Host | multi-vhost | enumerate names |

## Falsifier

Falsifier — every Host variant returns the same content: single vhost, nothing hidden behind routing.
