# Internal vhosts and loopback-only routes

Routes that exist only on internal hostnames or the loopback interface — disclosure finds them named in configs/comments.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| config/comment names an internal host | a vhost exists | Host-probe it |
| route present in source but 404s externally | loopback-only | backend-fetch chain |
| admin.* or dev.* subdomain in cert/comment | subdomain surface | probe it |

## Steps

1. Collect internal names from: configs, comments, certs, headers, JS.
2. Host-probe each name against the supplied target.
3. A loopback-only route reached via the backend itself = SSRF-adjacent; that's web-ssrf's chain.
4. Subdomains in scope get the same bounded sweep.

## Falsifier

Falsifier — no internal names exist in any leaked material: nothing to probe.

## Traps

- Only probe names the evidence produced — don't invent vhosts.
- Loopback routes via the app's own fetch are web-ssrf, not this class.
- dev/admin vhosts often skip auth entirely.

## Commands

```bash
curl -s -H 'Host: admin.internal' '$BASE/'
```

## Cross-references

`host-header-probes.md` · `../web-ssrf/`
