# Exposed .git — repository reconstruction

A served .git directory is the highest-value disclosure: full source, history, and every secret ever committed. Two access modes — the smart protocol (git clone) or loose-object walking when only static files are served.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.git/HEAD returns 'ref: refs/heads/...' | loose refs readable | git_dumper walk |
| git clone --no-checkout works | smart protocol exposed | clone + checkout |
| /.git/config 403 but HEAD 200 | partial exposure | per-file probing |
| packed-refs + objects/pack/*.pack | pack-only repo | honest partial recovery |

## Steps

1. Probe /.git/HEAD — a 'ref:' body confirms real git data, not a catch-all.
2. Try git clone --no-checkout <base>/.git; if the smart protocol answers, checkout and read.
3. Else: python3 tools/web/git_dumper.py --base <BASE>/.git/ --out repo — resolves HEAD, walks commit->tree->blob, inflates loose objects.
4. Read the recovered tree for secrets, endpoints, and the flag path.
5. Check git history: deleted secrets stay in earlier commits (git log -p).

## Falsifier

Falsifier — /.git/HEAD returns the app HTML (catch-all) or a 403/404 on every object path: no real repository is served. A 403 on config alone is not a falsifier — object paths may still read.

## Traps

- A catch-all 200 echoing the app shell is not a .git — the HEAD body must literally start 'ref:'.
- Pack-only repos (no loose objects) report honestly incomplete — objects in packfiles need the pack protocol, not file walks.
- git_dumper writes to --out; don't run it into the challenge's own directory.
- Secrets found in history are still secrets — redact before they touch the repo.

## Commands

```bash
python3 tools/web/git_dumper.py --base 'https://t/.git/' --out repo
python3 tools/web/git_dumper.py --selftest
```

## Cross-references

`tools-git-dumper.md` · `version-control-metadata.md` · `env-config-leaks.md`
