# Verification workflow — candidate to confirmed, step by step

## Step 1: the candidate

An anomaly — a `diff` line, a timing delta, a `Location` param, a
`code` field, a `Set-Cookie` — is a CANDIDATE, not a verdict. It names
the channel to verify.

## Step 2: the three arms

```bash
KNOWN=admin   FAKE=zzz-$(date +%s)   FAKE2=qqq-$(date +%s)
# run the channel's protocol on all three
```

- `KNOWN` vs `FAKE` — the oracle candidate (the delta)
- `FAKE` vs `FAKE2` — must be IDENTICAL (rules out request-noise)

If `b` and `b2` differ → the delta is noise, not the username-class;
discard the candidate and widen the mask.

## Step 3: the channel protocol

- body → the masked raw-byte diff (`response-diffing.md`)
- status+`Location` → `-D -`, never follow (`channel-status.md`)
- timing → N>=8 interleaved medians + jitter (`timing-statistics.md`)
- side → `-sv` envelope + send + lock (`channel-side.md`)
- direct → `?u=KNOWN`/`?u=FAKE` boolean (`api-enum.md`)

## Step 4: the re-run

Re-run the candidate measurement on a fresh session. A verdict requires
the delta to REPEAT — a single-run delta could be a transient.

## Step 5: the mask-validation

Is the surviving byte-diff STABLE across re-runs? A nonce/token/timestamp
that survives your mask is a false positive — widen the mask until the
diff is only the username-dependent byte.

## Step 6: the cross-form check

Does the oracle hold on the OTHER forms? A `/login`-only oracle is one
cell; register/reset/check/api/graphql may differ. Record per-cell.

## Step 7: the verdict grammar

```
oracle: <form>:<channel>   — the confirmed differential, verbatim
uniform: <form>:<channel>  — a measured-identical cell
unmeasured: <form>:<channel> — a gap to probe
candidate: <form>:<channel> — an anomaly, unverified
```

## Step 8: the name verification

A verified account name needs ITS oracle excerpt:

```
name: admin — confirmed via /api/username-available {"available":false}
name: service — confirmed via /login:timing (delta 47x jitter)
```

Never "admin probably exists" — the verbatim oracle per name.

## Step 9: the negative verification

A closed cell needs its measured uniform — `uniform: /login:body
(masked diff empty, three arms)` — not "looked the same".

## Step 10: the route

Each `oracle`/`name`/`throttle` finding routes to the neighbor:
- a verified name → `web-auth-session`/`web-idor`/`web-oauth-sso`
- a throttle `absent`/`bypassed` → `web-auth-session` (the spray)
- a uniform cell → a recorded negative in `../field-notes.md`

## The verification contract

A signal is a candidate until: three arms + the channel protocol + a
re-run confirm it. A flag counts only through `hooks.py pre-flag`. The
enum's output is a VERIFIED name and a MEASURED throttle — never a
claim from a single or unmasked response.
