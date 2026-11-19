# .env variant enumeration

The .env file has a family: .env.local, .env.production, .env.development, .env.bak, .env.old, .env.save, .env.example — each with different exposure rules.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /.env 403 but /.env.bak 200 | backup variant wins | read it |
| /.env.production vs /.env.local | environment variants | production secrets |
| /.env.example with real values | dev left real values | read it |

## Steps

1. Probe the family: .env .env.local .env.production .env.development .env.bak .env.old .env.save .env.example .env.sample .env.dev .env.test .env.prod.
2. A 403 on .env often doesn't extend to the variants.
3. .env.example with real values is a developer mistake.
4. Each variant gets the catch-all diff — 200-with-HTML is not a hit.

## Falsifier

Falsifier — every variant returns catch-all/404: no .env exposure.

## Traps

- Dot-file rules block .env but not .env.bak — the suffix bypasses the rule.
- The .env.example is MEANT to be safe; real values inside are the bug.
- Environment-specific files name the deployment's secrets.

## Commands

```bash
for p in /.env /.env.bak /.env.old /.env.local /.env.production /.env.example; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`env-config-leaks.md` · `static-leftovers.md`
