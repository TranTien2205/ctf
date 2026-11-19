# Error pages — stack traces and verbose errors — operational checklist

Verbose errors leak file paths, framework versions, query strings, line numbers, and sometimes code context. Trigger them deliberately with malformed input.

## Checklist

- [ ] Trigger errors: bad types (?id=abc into an int param), missing params, oversized values, malformed JSON.
- [ ] Read the whole error — the path, the class names, the framework signature.
- [ ] Extract: webroot path, framework+version, internal hostnames, query structure.
- [ ] Each extracted fact routes to a depth class: version → CVE lookup, path → file-read, query → sqli.

## Abort conditions

- A 500 with a generic page is not disclosure — you need internals in the body.
- Error pages behind a CDN may be normalized; try direct-host probes if given.
- Don't confuse 'page not found' styling with framework internals.

## Falsifier

Falsifier — all error paths return a generic branded error page with no internals: verbose errors are off. The channel is closed.

## Cross-references

`detection-matrix.md` · `debug-endpoints.md` · `header-disclosure.md`
