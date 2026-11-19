# Host and forwarded-header probing

The app's trust in Host/X-Forwarded-Host splits internal vs external views — some artifacts only serve to the internal name.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Host: internal-name returns different content | vhost routing | the internal vhost |
| X-Forwarded-Host: localhost flips a 403 | host allowlist | read the restricted path |
| Server: header changes with Host | multi-vhost | enumerate names |

## Steps

1. Re-request key artifacts with Host: localhost, Host: 127.0.0.1, Host: internal.
2. Try X-Forwarded-Host / X-Forwarded-Server / X-Host on 403s.
3. A different response under a different Host = a vhost finding.
4. Captured vhost names feed further Host probing.

## Falsifier

Falsifier — every Host variant returns the same content: single vhost, nothing hidden behind routing.

## Traps

- Don't invent hostnames — use names leaked by certs, comments, headers.
- This boundary is shared with web-host-header — deeper attacks live there.
- A 403→200 flip under Host: localhost is a real misconfig.

## Commands

```bash
curl -s -H 'Host: localhost' '$BASE/admin' ; curl -s -H 'X-Forwarded-Host: 127.0.0.1' '$BASE/.env'
```

## Cross-references

`../web-host-header/` · `alternate-verbs.md`
