# Exposed .git — repository reconstruction — index

A served .git directory is the highest-value disclosure: full source, history, and every secret ever committed. Two access modes — the smart protocol (git clone) or loose-object walking when only static files are served.

## Related modules

- `git-exposure-deep.md` — mechanism internals and boundary conditions
- `git-exposure-checklist.md` — the ordered operational steps
- `git-exposure-catalogue.md` — case enumeration

## Cross-references

`tools-git-dumper.md` · `version-control-metadata.md` · `env-config-leaks.md`
