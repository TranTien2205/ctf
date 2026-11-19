# Input transports — where the smash's bytes come from — case catalogue

stdin, argv, env, a socket, a file — each transport carries the payload with its own byte restrictions and re-trigger semantics.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | stdin read (fgets/read/scanf) | stdin transport | send + newline |
| 2 | argv[1] used directly | argv transport | arg = payload |
| 3 | getenv + copy | env transport | env var = payload |
| 4 | socket read | network transport | nc/python socket |
| 5 | fread from a file | file transport | write the file |

## Falsifier

Falsifier — the transport isn't what you assumed (e.g., it's a socket field, not stdin): the byte-filtering/re-trigger rules change.
