# Internal vhosts and loopback-only routes — checklist

Routes that exist only on internal hostnames or the loopback interface — disclosure finds them named in configs/comments.

## Checklist

- [ ] Collect internal names from: configs, comments, certs, headers, JS.
- [ ] Host-probe each name against the supplied target.
- [ ] A loopback-only route reached via the backend itself = SSRF-adjacent; that's web-ssrf's chain.
- [ ] Subdomains in scope get the same bounded sweep.

## Abort conditions

- Only probe names the evidence produced — don't invent vhosts.
- Loopback routes via the app's own fetch are web-ssrf, not this class.
- dev/admin vhosts often skip auth entirely.

## Falsifier

Falsifier — no internal names exist in any leaked material: nothing to probe.
