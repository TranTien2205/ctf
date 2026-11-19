# Throttling (deep) — the loop-bound, fully worked

## The control taxonomy

| Control | Where | The counter-key |
|---|---|---|
| rate limit | per-IP / per-session / per-endpoint | source-IP / cookie / route |
| account lockout | per-account | the username |
| progressive delay | per-account / per-IP | attempt count |
| CAPTCHA | per-IP / per-account | after N |
| IP ban | per-IP | source-IP, temp block |
| global budget | shared | rare |

## Measuring each — the bounded protocol

```bash
# the absent/threshold burst — 15 requests
for i in $(seq 15); do curl -s -o /dev/null -w "$i %{http_code} %{time_total}\n" \
  -X POST -d "user=t$i&pass=x" "$BASE/login"; done
```

- all `200`/`401` flat → absent
- `429`/`423` at N → the threshold; record N
- growing `time_total` → a progressive delay
- a CAPTCHA/redirect → the challenge control
- a `403`/`blocked` after a burst → an IP ban

## The lockout-as-oracle — the measured proof

A lockout that fires only on a real row IS an exists-oracle:

```bash
for u in "$KNOWN" "$FAKE"; do
  for i in $(seq 12); do curl -s -o /dev/null -w "$u $i %{http_code}\n" \
    -X POST -d "user=$u&pass=x" "$BASE/login"; done
done
# KNOWN -> 423 at attempt N ; FAKE -> 200/401 forever => the lock oracle
```

## The counter-key hunt

Which key does the counter use? Probe by rotating ONE:

- rotate `X-Forwarded-For` → if `429` resets, per-IP
- drop the session cookie → if `429` resets, per-session
- rotate the username → if `429` never fires per-name, per-account
- hit `/api/login` after `/login` `429`s → if `200`, per-endpoint

## The bypass verdicts

- `X-Forwarded-For: <rand>` → `200`/`401` post-`429` → per-IP bypassed
- fresh session → `200` → per-session bypassed
- a different route (`/api/login`) → `200` → per-endpoint gap
- `GET`/JSON/case → `200` → a method/param/case gap
- a per-second window → `1/sec` sustained → a window, not a block

The bypass is the finding — record `<key> resets the counter`, not the
spray.

## The per-account spray-under

A per-account lock at N → one password per account across M accounts
stays under it. This is the password-spraying pattern — a confirmed
account list + one common password. The finding is the per-account
bound; the spray is `web-auth-session`'s.
