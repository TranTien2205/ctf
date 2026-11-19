# Error pages — stack traces and verbose errors — case catalogue

Verbose errors leak file paths, framework versions, query strings, line numbers, and sometimes code context. Trigger them deliberately with malformed input.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | Stack trace with file paths | debug error handling | paths for traversal/class clues |
| 2 | Query echoed in SQL error | sqli confirmation too | hands to web-sqli |
| 3 | 'Powered by X version Y' in error page | version fingerprint | CVE/versioned attacks |
| 4 | Path like /var/www/app/... in a trace | webroot location | file-read/traversal chains |

## Falsifier

Falsifier — all error paths return a generic branded error page with no internals: verbose errors are off. The channel is closed.

## Coverage notes

- A 500 with a generic page is not disclosure — you need internals in the body.
- Error pages behind a CDN may be normalized; try direct-host probes if given.
- Don't confuse 'page not found' styling with framework internals.
- A leaked framework version is a lead, not a bug — still needs a route to impact.

## Cross-references

`detection-matrix.md` · `debug-endpoints.md` · `header-disclosure.md`
