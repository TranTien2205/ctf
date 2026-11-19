# Header and banner disclosure — case catalogue

Response headers leak framework, version, internal routing, and caching structure — free recon in every response, before any probing.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | X-Powered-By: Express/4.x | framework+version | version-specific routes |
| 2 | Server: nginx/1.x | server stack | proxy-chain hints |
| 3 | Server-Timing or X-Debug-* | internals exposed | deeper debug surface |
| 4 | X-Backend/X-Upstream/X-Real-IP set | proxy topology | smuggling/parser-differential leads |
| 5 | X-Generator, X-Drupal-Cache, X-Varnish | platform fingerprint | platform attack surface |

## Falsifier

Falsifier — headers are stripped to nothing informative: the disclosure channel is silent; fingerprint from body/error content instead.

## Coverage notes

- 'Server: nginx' under a reverse proxy says nothing about the app — check X-Powered-By and framework signatures in the body.
- Header values can be decoys (a 'Apache/2.4' on a Node app); corroborate with error pages.
- CORS/security headers matter for other classes — note them while you're here.

## Cross-references

`error-pages.md` · `detection-matrix.md`
