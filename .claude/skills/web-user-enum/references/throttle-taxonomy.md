# Throttle taxonomy — every control, keyed and measured

## By counter-key — what increments

| Control | Key | The reset vector |
|---|---|---|
| per-IP rate limit | source-IP | `X-Forwarded-For`/`X-Real-IP`/proxy-rotate |
| per-session rate limit | session cookie | a fresh cookie/incognito |
| per-account lockout | the username | a different account (spray-under) |
| per-endpoint limit | the route | an alias `/login`→`/api/login` |
| per-method limit | HTTP method | `GET`/`PUT` vs `POST` |
| per-param limit | a param name | `user` vs `username` vs `email` |
| global/shared budget | all of the above | rare; the burst still bounds |
| progressive delay | attempt count | none — a delay, not a block |

## By mechanism — what fires

| Control | The observable | The measurement |
|---|---|---|
| `429 Too Many Requests` | a `429` status at N | the burst count |
| `423 Locked` | a `423` on a real row | the lock count on YOUR acct |
| `403`/IP-ban | a `403`/`blocked` after a burst | the burst to ban |
| CAPTCHA | an interstitial challenge after N | the N to the challenge |
| progressive delay | growing `time_total` | the delay curve |
| a fixed window | `1/sec`/`N/min` sustained | N per T measured |
| silent drop | a hang/timeout after N | the burst to drop |

## The measurement commands

```bash
# the absent/threshold burst — 15 requests
for i in $(seq 15); do curl -o /dev/null -w "$i %{http_code} %{time_total}\n" -X POST -d "user=t$i&pass=x" "$BASE/login"; done
# the lock — YOUR OWN account
for i in $(seq 12); do curl -o /dev/null -w '%{http_code} ' -X POST -d "user=$OWN&pass=wrong" "$BASE/login"; done
# the counter-key — rotate one variable
for h in X-Forwarded-For X-Real-IP X-Client-IP; do curl -o /dev/null -w '%{http_code} ' -H "$h: $RANDOM.$RANDOM.$RANDOM.$RANDOM" -d 'user=x&pass=y' "$BASE/login"; done
# fresh session / alias / method / content-type
curl -o /dev/null -w '%{http_code}\n' -X POST -d 'user=x&pass=y' "$BASE/login"
curl -o /dev/null -w '%{http_code}\n' -X POST -d 'user=x&pass=y' "$BASE/api/login"
curl -o /dev/null -w '%{http_code}\n' -X GET "$BASE/login?user=x&pass=y"
curl -o /dev/null -w '%{http_code}\n' -H 'Content-Type: application/json' -d '{"username":"x","password":"y"}' "$BASE/login"
```

## The verdict taxonomy

| Result | Verdict | The report |
|---|---|---|
| no control in 15 | `throttle: absent` | unbounded credential loop |
| `429`/`423` at N | `throttle: at-N` | a bound at N |
| `XFF`/fresh/alias/method resets | `throttle: bypassed-by-<key>` | a broken control |
| a `1/sec` window | `throttle: window-N-per-T` | a bound, not a block |
| a CAPTCHA | `throttle: captcha-at-N` | a challenge after N |
| a per-account lock | `throttle: per-account-at-N` + `oracle: lock` | the lock IS the oracle |

## The distributed-scope taxonomy

- a per-worker counter — `429` at inconsistent counts (the counter is
  not shared across workers) — `distributed-and-cache.md`
- a global counter — `429` at a fixed N regardless of source — a real
  bound
- a `X-RateLimit-*`/`Retry-After` header — names the counter-key and
  the window without the burst

## The throttle-is-the-oracle rule

A lockout is BOTH a control AND an existence-oracle — `423` on real,
`401` on fake. Never treat the lock as "the defense won" — record
`locks at N` + the confirmed name; the lock's existence proves the
account's existence.
