# Exposed .git — repository reconstruction — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.git/HEAD returns 'ref: refs/heads/...' | loose refs readable | git_dumper walk |
| git clone --no-checkout works | smart protocol exposed | clone + checkout |
| /.git/config 403 but HEAD 200 | partial exposure | per-file probing |
| packed-refs + objects/pack/*.pack | pack-only repo | honest partial recovery |

## Falsifier

Falsifier — /.git/HEAD returns the app HTML (catch-all) or a 403/404 on every object path: no real repository is served. A 403 on config alone is not a falsifier — object paths may still read.
