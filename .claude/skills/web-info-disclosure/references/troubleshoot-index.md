# Troubleshooting — symptom → cause → fix — index

| Symptom | Likely cause | Fix |
|---|---|---|
| every path 200 same size | catch-all | diff body against baseline |
| .git/HEAD 403 | partial exposure | probe HEAD/objects directly |
| git_dumper finds only refs | pack-only repo | honest partial — note it |
| archive 200 but won't extract | catch-all or truncated | check magic bytes |
| .env 403 | dot-file rule | try .env.bak/.env.old |
| bundle_miner finds no map | no map shipped | mine minified bundle anyway |
| actuator root 404 | per-endpoint exposure | probe /actuator/env directly |
| headers say nothing | stripped | fingerprint from body/errors |
| 403 on a real path | forbidden not absent | other verbs, Host tricks |
| 'index of' page 403s | listing on other dirs | probe sibling dirs |


## Related modules

- `troubleshoot-deep.md` — mechanism internals and boundary conditions
- `troubleshoot-checklist.md` — the ordered operational steps
- `troubleshoot-catalogue.md` — case enumeration

## Cross-references

`catchall-falsifier.md`
