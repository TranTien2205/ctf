# Troubleshooting — symptom → cause → fix — deep

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


## Mechanism internals

A disclosure channel is only as real as the byte-diff it produces against the catch-all baseline. Every finding reduces to: a path returned content the absent-path baseline did not. Channels differ only in WHERE the content lives — a file, an index page, an error body, a header — not in the proof shape.

## Boundary conditions

- Catch-all servers make status meaningless; only body-diff counts.
- A 403 on a real artifact is exposure-in-progress, not absence — try sibling names/verbs.
- Huge artifacts (dumps, heapdumps) are grepped, not read.
- Recovered credentials are evidence to note, never to commit.
- A channel whose falsifier fires is closed for this challenge — record and move on.

## Falsifier

--

## Cross-references

`catchall-falsifier.md`
