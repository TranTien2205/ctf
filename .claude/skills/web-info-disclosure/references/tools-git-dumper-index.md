# tools/web/git_dumper.py — loose-object recovery — index

Reconstructs a served .git over plain HTTP when the smart protocol isn't available: resolves HEAD, walks commit->tree->blob, inflates each loose object into a working tree.

## Related modules

- `tools-git-dumper-deep.md` — mechanism internals and boundary conditions
- `tools-git-dumper-checklist.md` — the ordered operational steps
- `tools-git-dumper-catalogue.md` — case enumeration

## Cross-references

`git-exposure.md` · `version-control-metadata.md`
