# tools/web/read_loop.py — proven file-read walks — operational checklist

When a read primitive already exists (a path param, an LFI), read_loop walks wordlists/profiles over it: config, secrets, flags, source profiles built in.

## Checklist

- [ ] The read primitive comes from file-read-primitives — this tool is the loop over it.
- [ ] --profile quick for a fast pass; secrets/config for targeted lists.
- [ ] --path <exact> when a filename is already known.
- [ ] --extract '<regex>' when the response wraps content in JSON/HTML.
- [ ] --extract-paths turns every absolute path found into a follow-up read.

## Abort conditions

- This is a file-read tool — the primitive must exist first; it doesn't discover paths.
- --encode double-url for double-decode filters.
- --no-baseline when the endpoint has no meaningful 404 baseline.

## Falsifier

Falsifier — the primitive reads nothing (all misses): the read isn't real or the paths are wrong.

## Cross-references

`../file-read-primitives/` · `bounded-sweep.md`
