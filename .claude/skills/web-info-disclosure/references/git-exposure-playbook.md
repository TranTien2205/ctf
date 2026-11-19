# Exposed .git — repository reconstruction — playbook

A served .git directory is the highest-value disclosure: full source, history, and every secret ever committed. Two access modes — the smart protocol (git clone) or loose-object walking when only static files are served.

## Ordered playbook

1. Probe /.git/HEAD — a 'ref:' body confirms real git data, not a catch-all.
2. Try git clone --no-checkout <base>/.git; if the smart protocol answers, checkout and read.
3. Else: python3 tools/web/git_dumper.py --base <BASE>/.git/ --out repo — resolves HEAD, walks commit->tree->blob, inflates loose objects.
4. Read the recovered tree for secrets, endpoints, and the flag path.
5. Check git history: deleted secrets stay in earlier commits (git log -p).

## Falsifier

Falsifier — /.git/HEAD returns the app HTML (catch-all) or a 403/404 on every object path: no real repository is served. A 403 on config alone is not a falsifier — object paths may still read.

## Commands

```bash
python3 tools/web/git_dumper.py --base 'https://t/.git/' --out repo
python3 tools/web/git_dumper.py --selftest
```
