# Throttling — the class's second half

## The question

Can the attacker run the enumeration/guessing loop unbounded? The
controls that bound it: **rate limiting** (per-IP, per-account,
per-session, per-endpoint), **lockout** (account freezes after N fails),
**CAPTCHA** (a challenge after N), **progressive delay** (each fail is
slower), **IP ban** (a temporary block).

The finding is either (a) a control is **absent** where it should be, or
(b) a control is **present but bypassable** — a header resets the counter.

## Proving absence — a bounded burst

```bash
for i in $(seq 12); do
  curl -s -o /dev/null -w "%{http_code} %{time_total}\n" \
    -X POST -d "user=test$i&pass=x" "$BASE/login"
done
```

The absence signal: 12+ requests, no `429`, no CAPTCHA challenge, no
growing delay, no lock. **Stop at 8-15** — more is a brute-force run,
not a measurement, and on a shared target it is the abuse the control
exists to stop.

## Proving a control — find the threshold

```bash
# on an account YOU control — find where the limit fires
for i in $(seq 1 20); do
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST -d "user=MYACCT&pass=x" "$BASE/login")
  echo "$i $code"; [ "$code" = "429" ] && break
done
```

The threshold N is the finding — record it (`locks at 8`, `429s at 20`).
A locked account is evidence FOR the control, not its absence — the
finding is what happens before the lock.

## Where the limit lives

- **per-IP** — `X-Forwarded-For` / a different source resets it
- **per-account** — the counter is keyed on the username; rotating usernames
  avoids it (password-spraying pattern)
- **per-session** — a fresh session/cookie resets it
- **per-endpoint** — `/login` is limited but `/api/login` or `/reset` is not
- **global** — a shared budget; rare

## The report shape

- absent: `no throttle: 15 reqs, no 429/captcha/lock`
- present: `locks at 8 per-account`, `429 at 20 per-IP`
- bypassed: `X-Forwarded-For resets the per-IP counter` — the bypass IS
  the finding (`rate-limit-bypass.md`)
