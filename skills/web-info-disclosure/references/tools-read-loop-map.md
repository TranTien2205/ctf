# tools/web/read_loop.py — proven file-read walks — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| --url contains {path} | the read primitive | from file-read class |
| --profile {all,config,container,flags,quick,secrets,source} | canned lists | pick the narrowest |
| --path reads exactly one | targeted | when a name is known |
| --extract pulls content from JSON/HTML wrappers | response unwrap | for JSON APIs |
| --extract-paths feeds found paths back | chaining | recursive discovery |

## Falsifier

Falsifier — the primitive reads nothing (all misses): the read isn't real or the paths are wrong.
