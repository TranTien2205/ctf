# tools/web/http_probe.py — the sanctioned request+response — deep

The one component that holds request and response together and emits the post-probe command with --response already filled — use it for disclosure probes so evidence is paste-free.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — the response is the catch-all body: no disclosure, record the negative.

## Highest-cost traps

- --emit writes state — only when the probe is real (not a rehearsal).
- --class must match the hypothesis bug_class or the hook refuses.

## Commands

```bash
python3 tools/web/http_probe.py --url '$BASE/.git/HEAD' --challenge ch --class web-info-disclosure --hypothesis-id h1 --emit
```

## Cross-references

`evidence.md` · `bounded-sweep.md`
