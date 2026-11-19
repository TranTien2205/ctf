# Exposed .git — repository reconstruction — deep

A served .git directory is the highest-value disclosure: full source, history, and every secret ever committed. Two access modes — the smart protocol (git clone) or loose-object walking when only static files are served.

## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

Falsifier — /.git/HEAD returns the app HTML (catch-all) or a 403/404 on every object path: no real repository is served. A 403 on config alone is not a falsifier — object paths may still read.

## Highest-cost traps

- A catch-all 200 echoing the app shell is not a .git — the HEAD body must literally start 'ref:'.
- Pack-only repos (no loose objects) report honestly incomplete — objects in packfiles need the pack protocol, not file walks.
- git_dumper writes to --out; don't run it into the challenge's own directory.

## Commands

```bash
python3 tools/web/git_dumper.py --base 'https://t/.git/' --out repo
python3 tools/web/git_dumper.py --selftest
```

## Cross-references

`tools-git-dumper.md` · `version-control-metadata.md` · `env-config-leaks.md`
