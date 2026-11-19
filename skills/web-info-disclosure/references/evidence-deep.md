# Evidence — disclosure proofs — deep

A disclosure finding's evidence is the artifact itself, verbatim. post-probe records the excerpt; pre-flag only on response bytes.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

--

## Highest-cost traps

- A catch-all 200 is NOT a finding — the content must differ from baseline.
- Tool output alone isn't evidence; the response bytes are.

## Commands

```bash
python3 tools/hooks.py post-probe <ch> --verdict confirms --hypothesis-id <id> --class web-info-disclosure --evidence-kind class --evidence 'ref: refs/heads/main' --response '<the bytes>'
```

## Cross-references

`catchall-falsifier.md`
