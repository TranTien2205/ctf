# tools/web/git_dumper.py — loose-object recovery — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| --base = the .git URL with trailing / | the endpoint | must serve object files |
| --out = local recovery dir | where the tree lands | scratch dir |
| --max-requests bounds the walk | rate limit | size to the target |
| --selftest proves the walker | offline check | run first |

## Falsifier

Falsifier — HEAD doesn't return 'ref:' or object paths 404: nothing to walk. The tool reports incompleteness honestly.
