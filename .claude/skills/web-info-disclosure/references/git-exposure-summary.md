# Exposed .git — repository reconstruction — summary

A served .git directory is the highest-value disclosure: full source, history, and every secret ever committed. Two access modes — the smart protocol (git clone) or loose-object walking when only static files are served.

## Signal → route

- /.git/HEAD returns 'ref: refs/heads/...' → git_dumper walk
- git clone --no-checkout works → clone + checkout
- /.git/config 403 but HEAD 200 → per-file probing
- packed-refs + objects/pack/*.pack → honest partial recovery

## Falsifier

Falsifier — /.git/HEAD returns the app HTML (catch-all) or a 403/404 on every object path: no real repository is served. A 403 on config alone is not a falsifier — object paths may still read.
