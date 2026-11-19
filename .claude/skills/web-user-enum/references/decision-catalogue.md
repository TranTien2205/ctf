# Decision catalogue — every branch, decided

## Start — which probe first?

```
the bundle names a check/available/users endpoint?
  yes -> Pass 2: probe it (cheapest, one request)
  no  -> Pass 3: the per-form channels
a register/reset exists?
  -> probe it (the built-to-reveal / send-side oracles)
```

## `KNOWN` vs `FAKE` differ on body

- a clear `"no such"`/`"wrong password"` → `oracle: body/text`
- a subtle `code`/class/`data-`/hidden/comment → `oracle: body/residual`
- → confirm with `FAKE2` identical to `FAKE`; record; move to the list

## identical body — next?

- check `status` + `Location` — a `?e=`/`?error=` param or a code diff
- check the `-sv` envelope — a `Set-Cookie`/`X-`/`attempts`/`emails`
- check timing — N>=8 medians + jitter
- if all uniform → `/login` (that form) is closed; move to register/reset

## a 50-300ms median delta

- `oracle: timing` — the verify-short-circuit
- confirm: `FAKE` vs `FAKE2` medians identical (not noise); a re-run
- record `good_med`/`bad_med`/`jitter`; move to the list

## a `429`/`423` mid-burst

- at N → `throttle: at-N`; record N
- a `423` only on real → `oracle: lock` (the lock IS the oracle)
- a `429` → the bypass probe (XFF/session/endpoint/method)

## `X-Forwarded-For`/fresh-session resets the `429`

- `throttle: bypassed-by-<key>` — the counter trusts attacker input
- the finding is the reset — record it; do NOT spray

## all forms, all channels uniform

- a real all-uniform negative → record every cell; the class is closed
- BUT first confirm the coverage matrix is complete — a `/login`-only
  read is not the class

## the oracle confirmed, the list run

- `verified: <name>` per `{"available":false}`/`200`/etc.
- each name → `exploitation.md` → the neighbor class
- the enum's budget ends at the route

## an injection-shaped differential

- an `admin'`/`{"$ne"}`/`{{7*7}}` that changes the response → a
  DIFFERENT class — route to `web-sqli`/`web-nosqli`/`web-ssti`; the
  enum's existence-measure is separate

## a `/api/users/{id}` 200

- the exists-oracle (enum) + the object read (`web-idor`) — both fire;
  record each as its own class

## a confirmed account + a weak pw / a reset / an SSO

- `web-auth-session` (the credential/reset/session), `web-oauth-sso`
  (the pre-hijack) — the enum names the account; the neighbor exploits

## Budget spent, no oracle

- the coverage matrix shows which cells are `unmeasured` — the next
  pass targets them; if all measured-uniform, the class is falsified;
  `tools/decide.py` escalation rung
