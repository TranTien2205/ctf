# tools/web/git_dumper.py — loose-object recovery

Reconstructs a served .git over plain HTTP when the smart protocol isn't available: resolves HEAD, walks commit->tree->blob, inflates each loose object into a working tree.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --base = the .git URL with trailing / | the endpoint | must serve object files |
| --out = local recovery dir | where the tree lands | scratch dir |
| --max-requests bounds the walk | rate limit | size to the target |
| --selftest proves the walker | offline check | run first |

## Steps

1. Confirm /.git/HEAD returns 'ref:' first — no real repo, no point.
2. python3 tools/web/git_dumper.py --base 'https://t/.git/' --out repo.
3. Inspect repo/ — the working tree plus any recoverable history.
4. A pack-only repo reports honestly incomplete — that IS the result; don't fabricate the rest.

## Falsifier

Falsifier — HEAD doesn't return 'ref:' or object paths 404: nothing to walk. The tool reports incompleteness honestly.

## Traps

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
