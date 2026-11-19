# Header and banner disclosure — deep

Response headers leak framework, version, internal routing, and caching structure — free recon in every response, before any probing.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — headers are stripped to nothing informative: the disclosure channel is silent; fingerprint from body/error content instead.

## Highest-cost traps

- 'Server: nginx' under a reverse proxy says nothing about the app — check X-Powered-By and framework signatures in the body.
- Header values can be decoys (a 'Apache/2.4' on a Node app); corroborate with error pages.
- CORS/security headers matter for other classes — note them while you're here.

## Commands

```bash
curl -sI '$BASE/' ; curl -s -D- -o /dev/null '$BASE/api'
```

## Cross-references

`error-pages.md` · `detection-matrix.md`
