# Header and banner disclosure

Response headers leak framework, version, internal routing, and caching structure — free recon in every response, before any probing.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| X-Powered-By: Express/4.x | framework+version | version-specific routes |
| Server: nginx/1.x | server stack | proxy-chain hints |
| Server-Timing or X-Debug-* | internals exposed | deeper debug surface |
| X-Backend/X-Upstream/X-Real-IP set | proxy topology | smuggling/parser-differential leads |
| X-Generator, X-Drupal-Cache, X-Varnish | platform fingerprint | platform attack surface |

## Steps

1. curl -sI the base URL and each interesting endpoint — read every header.
2. Record Server, X-Powered-By, X-AspNet-Version, X-Generator, Via, X-Cache.
3. Fingerprint the framework; route to that framework's debug/actuator list.
4. Proxy headers (Via, X-Forwarded-*, X-Upstream) hint at smuggling/parser-differential.

## Falsifier

Falsifier — headers are stripped to nothing informative: the disclosure channel is silent; fingerprint from body/error content instead.

## Traps

- 'Server: nginx' under a reverse proxy says nothing about the app — check X-Powered-By and framework signatures in the body.
- Header values can be decoys (a 'Apache/2.4' on a Node app); corroborate with error pages.
- CORS/security headers matter for other classes — note them while you're here.

## Commands

```bash
curl -sI '$BASE/' ; curl -s -D- -o /dev/null '$BASE/api'
```

## Cross-references

`error-pages.md` · `detection-matrix.md`
