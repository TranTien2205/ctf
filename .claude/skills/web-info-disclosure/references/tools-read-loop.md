# tools/web/read_loop.py — proven file-read walks

When a read primitive already exists (a path param, an LFI), read_loop walks wordlists/profiles over it: config, secrets, flags, source profiles built in.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --url contains {path} | the read primitive | from file-read class |
| --profile {all,config,container,flags,quick,secrets,source} | canned lists | pick the narrowest |
| --path reads exactly one | targeted | when a name is known |
| --extract pulls content from JSON/HTML wrappers | response unwrap | for JSON APIs |
| --extract-paths feeds found paths back | chaining | recursive discovery |

## Steps

1. The read primitive comes from file-read-primitives — this tool is the loop over it.
2. --profile quick for a fast pass; secrets/config for targeted lists.
3. --path <exact> when a filename is already known.
4. --extract '<regex>' when the response wraps content in JSON/HTML.
5. --extract-paths turns every absolute path found into a follow-up read.

## Falsifier

Falsifier — the primitive reads nothing (all misses): the read isn't real or the paths are wrong.

## Traps

- This is a file-read tool — the primitive must exist first; it doesn't discover paths.
- --encode double-url for double-decode filters.
- --no-baseline when the endpoint has no meaningful 404 baseline.

## Commands

```bash
python3 tools/web/read_loop.py --url 'https://t/f?p={path}' --profile secrets
python3 tools/web/read_loop.py --url 'https://t/f?p={path}' --path /etc/flag
```

## Cross-references

`../file-read-primitives/` · `bounded-sweep.md`
