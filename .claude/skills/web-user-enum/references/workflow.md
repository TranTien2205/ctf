# Workflow — the ordered pass

## Phase 0: scope + account inventory

- is this an authorized/owned/lab target? (spray is scope-gated)
- known-good: your account, a seeded `admin`, a challenge-named user
- the account-touching forms: login, register, reset, check-username,
  forgot-username, mfa, `/api/*`, graphql — `form-surface.md`

## Phase 1: the three-request oracle probe (per form)

```bash
curl -i -X POST -d 'user=KNOWN&pass=x'      "$BASE/<form>" > good
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad1
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad2
```

Or `enum_probe`:

```bash
python3 tools/web/enum_probe.py --url "$BASE/<form>" \
  --body 'user={U}&pass=x' --known-user KNOWN --method POST
```

## Phase 2: channel measurement (per form)

- body: `diff <(noise-masked good) <(noise-masked bad1)`
- status+redirect: `grep -iE '^HTTP|^location' good bad1`
- timing: N≥8 interleaved median delta — `timing-oracle.md`
- side: `-sv` envelope diff — `channel-side.md`

## Phase 3: confirm the oracle

- `bad1==bad2` (noise baseline), `good!=bad` on ≥1 channel
- a second bad name → same as `bad1` (tracks the username-class)
- a re-run → the delta repeats

## Phase 4: throttle measurement

- bounded burst (8-15) → absent / threshold / `429`/`423`/captcha
- if a limit fires → `rate-limit-bypass.md` (X-Forwarded-For, fresh
  session, endpoint/method/param rotation)

## Phase 5: the account list (bounded)

On an authorized target, a confirmed oracle + a bounded candidate list
→ the verified account names. Never a mass spray — the throttle
measurement bounds it; on a shared target, confirm your own account
plus one seeded name only.

## Phase 6: record + route

- `enum: <form>: <channel>: <delta>` per confirmed oracle
- each confirmed account routed to `web-auth-session`/`web-idor`/
  `web-logic-flaw`/`web-oauth-sso`
- a no-throttle or a bypassed-limit finding recorded with the count
- a uniform all-forms result → a recorded negative

## The bounded rule

The pass ends when every account-touching form is measured
oracle-or-uniform AND the throttle is measured absent/present/bypassed.
Do not re-probe a closed channel; do not spray — the enum is the
measurement, not the brute force.
