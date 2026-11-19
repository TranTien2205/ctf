# Reporting — the finding format and the record

## The oracle finding — the report shape

```markdown
## User enumeration — <form>:<channel>

**Endpoint:** POST /api/login
**Channel:** timing (the verify-short-circuit)

**Evidence:**
  KNOWN (admin):  median 247ms, N=16
  FAKE  (zzz-x):  median 9ms,   N=16
  FAKE2 (qqq-x):  median 9ms,   N=16
  jitter baseline: 5ms  →  delta 238ms = 47x jitter (repeated)

**Impact:** confirms which usernames exist → enables targeted
credential-stuffing / reset attacks on verified accounts.

**Confirmed accounts:** admin, service, flag (via the timing oracle)
```

## The throttle finding — the report shape

```markdown
## Missing rate limit on /login

**Endpoint:** POST /login
**Result:** 15 consecutive auth attempts, no 429/423/CAPTCHA/delay
**Impact:** an unbounded credential-guessing loop is possible — a
confirmed account can be brute-forced without a countermeasure.
```

```markdown
## Rate-limit bypass — per-IP counter trusts X-Forwarded-For

**Result:** 429 at attempt 9 per source-IP; an arbitrary
`X-Forwarded-For: <rand>` resets the counter → the limit never fires.
**Impact:** the per-IP throttle is bypassable → unbounded spray.
```

## The record — `../field-notes.md` entries

```
enum: /login:timing  ->  247ms vs 9ms (47x jitter)   [confirmed]
enum: /register:text ->  "username already taken"    [confirmed]
name: admin,service,flag  via /login:timing          [confirmed]
throttle: /login  absent (15-burst, no 429/lock)     [confirmed]
throttle: /api/login  per-IP at 8, bypassed by XFF   [confirmed]
negative: /login:body  uniform (masked diff, 3 arms) [recorded]
negative: /api/users/{id}  404 for both arms         [recorded]
route:  admin/service/flag -> web-auth-session
```

## The chain-card handoff

A verified enum→exploit chain produces a card:

```
chain: web-user-enum(oracle) -> verified(admin) -> web-auth-session(weak-pw) -> flag
signals: /login returns a timing gap on real users (verify-short-circuit)
probe:   N>=8 interleaved median timing on /login; the seeded list
falsifier: all channels uniform on all account forms
blast_radius: the spray is bounded by the measured throttle; the lock
             oracle is measured on an owned account only
```

## The honest-negative report

```markdown
## User enumeration — not present (measured negative)

**Coverage:** /login, /register, /forgot, /check-username, /api/users/{id}, /graphql
**Result:** all channels uniform on every form —
  body/status/Location/envelope identical (masked, 3 arms);
  timing medians + variances equalized (dummy-hash confirmed by stdev);
  no send-side; no lock; no secondary-form oracle.
**Verdict:** the existence-oracle is closed on this surface.
```

## The reporting rule

A finding is the verbatim delta + the three-arm verification + the
impact + the route. A negative is the measured uniform + the coverage.
Never a claim from a single response, never the catalogue presented as
a local solve, never a flag without `hooks.py pre-flag`.
