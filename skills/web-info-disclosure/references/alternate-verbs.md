# 403 bypasses — verbs, headers, path tricks

A 403 on a real artifact is 'forbidden', not 'absent': alternate verbs, Host tricks, and path forms reopen it.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| GET 403 → HEAD/OPTIONS 200 | verb bypass | read body via the verb that answers |
| 403 → 200 with X-Forwarded-For: 127.0.0.1 | IP allowlist bypass | spoof the trusted header |
| 403 → 200 via /./path or //path | normalization gap | path tricks |
| 403 on /admin → 200 on /admin/ | trailing-slash rule | siblings |

## Steps

1. On every 403 in the bounded list: try HEAD, OPTIONS, POST.
2. Try trusted headers: X-Forwarded-For, X-Real-IP, X-Original-URL, X-Rewrite-URL.
3. Try path variants: //path, /./path, /path/, /path%2f.
4. A flip to 200/redirect is a finding AND a route in.

## Falsifier

Falsifier — every verb/header/path variant returns the same 403: the artifact is genuinely forbidden to this surface.

## Traps

- X-Original-URL/X-Rewrite-URL let a proxy route you around the ACL.
- Semicolon and %2e tricks work on Java/Apache stacks.
- A 403→302 to login means auth-gated, not forbidden.

## Commands

```bash
curl -s -o /dev/null -w '%{http_code}\n' -X OPTIONS '$BASE/.env'
curl -s -H 'X-Forwarded-For: 127.0.0.1' '$BASE/admin'
```

## Cross-references

`response-anatomy.md` · `../web-parser-differential/`
