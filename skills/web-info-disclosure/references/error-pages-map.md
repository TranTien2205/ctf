# Error pages — stack traces and verbose errors — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Stack trace with file paths | debug error handling | paths for traversal/class clues |
| Query echoed in SQL error | sqli confirmation too | hands to web-sqli |
| 'Powered by X version Y' in error page | version fingerprint | CVE/versioned attacks |
| Path like /var/www/app/... in a trace | webroot location | file-read/traversal chains |

## Falsifier

Falsifier — all error paths return a generic branded error page with no internals: verbose errors are off. The channel is closed.
