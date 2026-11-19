# tools/web/read_loop.py — proven file-read walks — deep

When a read primitive already exists (a path param, an LFI), read_loop walks wordlists/profiles over it: config, secrets, flags, source profiles built in.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — the primitive reads nothing (all misses): the read isn't real or the paths are wrong.

## Highest-cost traps

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
