# tools/web/read_loop.py — proven file-read walks — case catalogue

When a read primitive already exists (a path param, an LFI), read_loop walks wordlists/profiles over it: config, secrets, flags, source profiles built in.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | --url contains {path} | the read primitive | from file-read class |
| 2 | --profile {all,config,container,flags,quick,secrets,source} | canned lists | pick the narrowest |
| 3 | --path reads exactly one | targeted | when a name is known |
| 4 | --extract pulls content from JSON/HTML wrappers | response unwrap | for JSON APIs |
| 5 | --extract-paths feeds found paths back | chaining | recursive discovery |

## Falsifier

Falsifier — the primitive reads nothing (all misses): the read isn't real or the paths are wrong.

## Coverage notes

- This is a file-read tool — the primitive must exist first; it doesn't discover paths.
- --encode double-url for double-decode filters.
- --no-baseline when the endpoint has no meaningful 404 baseline.

## Cross-references

`../file-read-primitives/` · `bounded-sweep.md`
