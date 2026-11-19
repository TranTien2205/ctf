# .env variant enumeration — checklist

The .env file has a family: .env.local, .env.production, .env.development, .env.bak, .env.old, .env.save, .env.example — each with different exposure rules.

## Checklist

- [ ] Probe the family: .env .env.local .env.production .env.development .env.bak .env.old .env.save .env.example .env.sample .env.dev .env.test .env.prod.
- [ ] A 403 on .env often doesn't extend to the variants.
- [ ] .env.example with real values is a developer mistake.
- [ ] Each variant gets the catch-all diff — 200-with-HTML is not a hit.

## Abort conditions

- Dot-file rules block .env but not .env.bak — the suffix bypasses the rule.
- The .env.example is MEANT to be safe; real values inside are the bug.
- Environment-specific files name the deployment's secrets.

## Falsifier

Falsifier — every variant returns catch-all/404: no .env exposure.
