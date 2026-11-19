# Workflow (deep) — the full pass, step by step

## Step 0: scope + known-good (the gate)

- confirm authorized/owned/lab — the spray is scope-gated
- register your account → a guaranteed known-good
- inventory the forms: `form-surface.md` — login/register/reset/check/
  forgot/unlock/mfa/invite/api/graphql/users-resource
- prep a provably-fake `zzz-<random>` and a SECOND different fake

## Step 1: the direct oracle (cheapest first)

```bash
curl -s "$BASE/api/username-available?u=KNOWN"
curl -s "$BASE/api/username-available?u=zzz-NOSUCH"
curl -s "$BASE/api/check-username?u=KNOWN"
curl -s -X POST -d 'user=KNOWN&email=a@b.c&pass=x' "$BASE/register"   # taken?
```

A `{"available":false}`/`{"taken":true}` → the class is confirmed in one
request. Skip the rest of the oracles; the list is next.

## Step 2: the 3-request pair per form

```bash
for form in login register forgot-password forgot-username unlock; do
  curl -i -X POST -d 'user=KNOWN&pass=x'      "$BASE/$form" > g.$form
  curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/$form" > b1.$form
  curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/$form" > b2.$form
done
```

## Step 3: the per-form channel measurement

```bash
# noise baseline
diff b1.$form b2.$form
# the masked body diff, the status+Location, the envelope
diff <(mask<g.$form) <(mask<b1.$form)
grep -iE '^HTTP|^location' g.$form b1.$form
diff <(grep set-cookie g.$form) <(grep set-cookie b1.$form)
# timing only if content is uniform — N>=8 interleaved
```

## Step 4: the oracle confirm

- `bad1==bad2` noise-masked, `good!=bad` on ≥1 channel
- a SECOND bad name → same response shape as `bad1`
- a re-run → the delta repeats
- record `<form>: <channel>: <verbatim delta>`

## Step 5: the throttle

```bash
for i in $(seq 15); do curl -s -o /dev/null -w '%{http_code} ' -X POST -d "user=t$i&pass=x" "$BASE/login"; done
```

absent / threshold-at-N / `423`/`429` → record; if limited →
`rate-limit-bypass.md` XFF/session/endpoint/method/param probes.

## Step 6: the bounded list

On a scoped target: 10-50 seeded names through the confirmed oracle →
the verified accounts. Never a mass wordlist; never over the throttle.

## Step 7: route + record

each name → `web-auth-session`/`web-idor`/`web-logic-flaw`/`web-oauth-sso`;
each throttle finding recorded; each uniform form recorded as a negative.
