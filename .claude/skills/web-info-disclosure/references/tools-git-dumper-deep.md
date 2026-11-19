# tools/web/git_dumper.py — loose-object recovery — deep

Reconstructs a served .git over plain HTTP when the smart protocol isn't available: resolves HEAD, walks commit->tree->blob, inflates each loose object into a working tree.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — HEAD doesn't return 'ref:' or object paths 404: nothing to walk. The tool reports incompleteness honestly.

## Highest-cost traps

- Trailing / on --base is required.
- Loose objects only — packfiles aren't fetched; the report says what's missing.
- --max-requests default may not fit the repo size — raise it if the walk truncates.

## Commands

```bash
python3 tools/web/git_dumper.py --selftest
python3 tools/web/git_dumper.py --base 'https://t/.git/' --out repo --max-requests 5000
```

## Cross-references

`git-exposure.md` · `version-control-metadata.md`
