# tools/web/id_sweep.py — existence oracle over ids — deep

Enumerates ids through a request template — for disclosure, useful when sequential ids expose other objects' data (which is also the web-idor boundary).

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — ids return uniform 404/catch-all: no enumerable surface.

## Highest-cost traps

- Sequential-id disclosure is web-idor's class when ownership matters — the tool is shared, the class differs.
- --stop-on-flag for flag-shaped responses.
- Respect --rate: shared infra, unbounded sweeps kill the instance.

## Commands

```bash
python3 tools/web/id_sweep.py --url 'https://t/doc/{id}' --range 1-500 --rate 5
python3 tools/web/id_sweep.py --url 'https://t/doc/{id}' --no-follow
```

## Cross-references

`bounded-sweep.md` · `../web-idor/`
