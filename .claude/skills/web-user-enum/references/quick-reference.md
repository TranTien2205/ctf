# Quick reference — the operator's card

## The probe

```bash
curl -i -X POST -d 'user=KNOWN&pass=x'      "$BASE/<form>" > good
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad1
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad2
python3 tools/web/enum_probe.py --url "$BASE/<form>" --body 'user={U}&pass=x' --known-user KNOWN
```

## The channels → the diff

| Channel | Command |
|---|---|
| body | `diff <(tr -s ' \t\n' ' ' <good) <(tr -s ' \t\n' ' ' <bad1)` |
| status+loc | `grep -iE '^HTTP\|^location' good bad1` |
| timing | `for i in {1..10}; do curl -s -o/dev/null -w '%{time_total}\n' -d "user=$u&pass=x" "$BASE/<f>"; done` |
| side | `curl -sv ... 2>&1 | grep -iE 'set-cookie|x-|HTTP'` |

## The oracle shapes

- `"no such user"` / `"wrong password"` / `"username taken"` — text
- `200` vs `302`, `?e=1` vs `?e=2`, `404` vs `401` — status/redirect
- `good` 50-300ms slower — timing (bcrypt gap)
- `{"error":"user_not_found"}`, `{"exists":true}`, a `Set-Cookie` — side

## The throttle

```bash
for i in {1..15}; do curl -s -o /dev/null -w '%{http_code}\n' -X POST -d "user=x$i&pass=y" "$BASE/login"; done
# no 429/lock/delay -> absent | N where 429/423 -> the threshold
# +X-Forwarded-For spoof resets -> bypassed (the finding)
```

## The route

`admin`/`service` confirmed → `web-auth-session` (spray/reset/MFA).
`/api/users/{name}` → `web-idor`. email collision → `web-oauth-sso`.
reset-flow → `web-logic-flaw`/`web-auth-session`.

## The falsifier

identical text+status+timing across known-good, known-bad, repeated-bad —
all four channels uniform → the form does not enumerate.

## The rules

repeated+channel-identified delta or it is not a finding · mask
per-request noise · N≥8 interleaved median for timing · never spray ·
catalogue class.
