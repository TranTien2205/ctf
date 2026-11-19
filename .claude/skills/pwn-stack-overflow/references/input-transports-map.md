# Input transports — where the smash's bytes come from — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| stdin read (fgets/read/scanf) | stdin transport | send + newline |
| argv[1] used directly | argv transport | arg = payload |
| getenv + copy | env transport | env var = payload |
| socket read | network transport | nc/python socket |
| fread from a file | file transport | write the file |

## Falsifier

Falsifier — the transport isn't what you assumed (e.g., it's a socket field, not stdin): the byte-filtering/re-trigger rules change.
