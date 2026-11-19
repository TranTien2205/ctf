# Header and banner disclosure — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| X-Powered-By: Express/4.x | framework+version | version-specific routes |
| Server: nginx/1.x | server stack | proxy-chain hints |
| Server-Timing or X-Debug-* | internals exposed | deeper debug surface |
| X-Backend/X-Upstream/X-Real-IP set | proxy topology | smuggling/parser-differential leads |
| X-Generator, X-Drupal-Cache, X-Varnish | platform fingerprint | platform attack surface |

## Falsifier

Falsifier — headers are stripped to nothing informative: the disclosure channel is silent; fingerprint from body/error content instead.
