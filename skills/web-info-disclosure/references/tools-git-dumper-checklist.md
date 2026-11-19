# tools/web/git_dumper.py — loose-object recovery — operational checklist

Reconstructs a served .git over plain HTTP when the smart protocol isn't available: resolves HEAD, walks commit->tree->blob, inflates each loose object into a working tree.

## Checklist

- [ ] Confirm /.git/HEAD returns 'ref:' first — no real repo, no point.
- [ ] python3 tools/web/git_dumper.py --base 'https://t/.git/' --out repo.
- [ ] Inspect repo/ — the working tree plus any recoverable history.
- [ ] A pack-only repo reports honestly incomplete — that IS the result; don't fabricate the rest.

## Abort conditions

- Trailing / on --base is required.
- Loose objects only — packfiles aren't fetched; the report says what's missing.
- --max-requests default may not fit the repo size — raise it if the walk truncates.

## Falsifier

Falsifier — HEAD doesn't return 'ref:' or object paths 404: nothing to walk. The tool reports incompleteness honestly.

## Cross-references

`git-exposure.md` · `version-control-metadata.md`
