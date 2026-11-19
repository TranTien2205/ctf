# Exposed .git — repository reconstruction — surface variants

A served .git directory is the highest-value disclosure: full source, history, and every secret ever committed. Two access modes — the smart protocol (git clone) or loose-object walking when only static files are served.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| /.git/HEAD returns 'ref: refs/heads/...' | loose refs readable | git_dumper walk |
| git clone --no-checkout works | smart protocol exposed | clone + checkout |
| /.git/config 403 but HEAD 200 | partial exposure | per-file probing |
| packed-refs + objects/pack/*.pack | pack-only repo | honest partial recovery |

## Variant-specific traps

- A catch-all 200 echoing the app shell is not a .git — the HEAD body must literally start 'ref:'.
- Pack-only repos (no loose objects) report honestly incomplete — objects in packfiles need the pack protocol, not file walks.
- git_dumper writes to --out; don't run it into the challenge's own directory.
- Secrets found in history are still secrets — redact before they touch the repo.

## Falsifier

Falsifier — /.git/HEAD returns the app HTML (catch-all) or a 403/404 on every object path: no real repository is served. A 403 on config alone is not a falsifier — object paths may still read.

## Cross-references

`tools-git-dumper.md` · `version-control-metadata.md` · `env-config-leaks.md`
