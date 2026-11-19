# tools/web/git_dumper.py — loose-object recovery — case catalogue

Reconstructs a served .git over plain HTTP when the smart protocol isn't available: resolves HEAD, walks commit->tree->blob, inflates each loose object into a working tree.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | --base = the .git URL with trailing / | the endpoint | must serve object files |
| 2 | --out = local recovery dir | where the tree lands | scratch dir |
| 3 | --max-requests bounds the walk | rate limit | size to the target |
| 4 | --selftest proves the walker | offline check | run first |

## Falsifier

Falsifier — HEAD doesn't return 'ref:' or object paths 404: nothing to walk. The tool reports incompleteness honestly.

## Coverage notes

- Trailing / on --base is required.
- Loose objects only — packfiles aren't fetched; the report says what's missing.
- --max-requests default may not fit the repo size — raise it if the walk truncates.

## Cross-references

`git-exposure.md` · `version-control-metadata.md`
