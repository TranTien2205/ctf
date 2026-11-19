# Exposed .git — repository reconstruction — operational checklist

A served .git directory is the highest-value disclosure: full source, history, and every secret ever committed. Two access modes — the smart protocol (git clone) or loose-object walking when only static files are served.

## Checklist

- [ ] Probe /.git/HEAD — a 'ref:' body confirms real git data, not a catch-all.
- [ ] Try git clone --no-checkout <base>/.git; if the smart protocol answers, checkout and read.
- [ ] Else: python3 tools/web/git_dumper.py --base <BASE>/.git/ --out repo — resolves HEAD, walks commit->tree->blob, inflates loose objects.
- [ ] Read the recovered tree for secrets, endpoints, and the flag path.
- [ ] Check git history: deleted secrets stay in earlier commits (git log -p).

## Abort conditions

- A catch-all 200 echoing the app shell is not a .git — the HEAD body must literally start 'ref:'.
- Pack-only repos (no loose objects) report honestly incomplete — objects in packfiles need the pack protocol, not file walks.
- git_dumper writes to --out; don't run it into the challenge's own directory.

## Falsifier

Falsifier — /.git/HEAD returns the app HTML (catch-all) or a 403/404 on every object path: no real repository is served. A 403 on config alone is not a falsifier — object paths may still read.

## Cross-references

`tools-git-dumper.md` · `version-control-metadata.md` · `env-config-leaks.md`
