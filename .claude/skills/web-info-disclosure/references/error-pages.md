# Error pages — stack traces and verbose errors

Verbose errors leak file paths, framework versions, query strings, line numbers, and sometimes code context. Trigger them deliberately with malformed input.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Stack trace with file paths | debug error handling | paths for traversal/class clues |
| Query echoed in SQL error | sqli confirmation too | hands to web-sqli |
| 'Powered by X version Y' in error page | version fingerprint | CVE/versioned attacks |
| Path like /var/www/app/... in a trace | webroot location | file-read/traversal chains |

## Steps

1. Trigger errors: bad types (?id=abc into an int param), missing params, oversized values, malformed JSON.
2. Read the whole error — the path, the class names, the framework signature.
3. Extract: webroot path, framework+version, internal hostnames, query structure.
4. Each extracted fact routes to a depth class: version → CVE lookup, path → file-read, query → sqli.

## Falsifier

Falsifier — all error paths return a generic branded error page with no internals: verbose errors are off. The channel is closed.

## Traps

- A 500 with a generic page is not disclosure — you need internals in the body.
- Error pages behind a CDN may be normalized; try direct-host probes if given.
- Don't confuse 'page not found' styling with framework internals.
- A leaked framework version is a lead, not a bug — still needs a route to impact.

## Commands

```bash
curl -s 'https://t/?id=abc' ; curl -s -X POST -H 'Content-Type: application/json' -d '{bad' 'https://t/api'
```

## Cross-references

`detection-matrix.md` · `debug-endpoints.md` · `header-disclosure.md`
