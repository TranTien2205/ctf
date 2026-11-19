# Header and banner disclosure — operational checklist

Response headers leak framework, version, internal routing, and caching structure — free recon in every response, before any probing.

## Checklist

- [ ] curl -sI the base URL and each interesting endpoint — read every header.
- [ ] Record Server, X-Powered-By, X-AspNet-Version, X-Generator, Via, X-Cache.
- [ ] Fingerprint the framework; route to that framework's debug/actuator list.
- [ ] Proxy headers (Via, X-Forwarded-*, X-Upstream) hint at smuggling/parser-differential.

## Abort conditions

- 'Server: nginx' under a reverse proxy says nothing about the app — check X-Powered-By and framework signatures in the body.
- Header values can be decoys (a 'Apache/2.4' on a Node app); corroborate with error pages.
- CORS/security headers matter for other classes — note them while you're here.

## Falsifier

Falsifier — headers are stripped to nothing informative: the disclosure channel is silent; fingerprint from body/error content instead.

## Cross-references

`error-pages.md` · `detection-matrix.md`
