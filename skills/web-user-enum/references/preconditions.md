# Preconditions — when this class applies

## Applies when

- the target has an account-touching endpoint: login, register, reset,
  forgot-username, check-username, mfa, invite, or an `/api/*` auth or
  user-resource route
- a username/email/account-name is a request input
- the question "does account X exist?" matters for the chain — a spray,
  a reset, an IDOR read, an SSO collision, a weak password

## Does NOT apply when — the confusable boundary

- a uniform-auth target with a **session/JWT/token bug** → `web-auth-session`
- a broken **business rule / workflow** (not an existence leak) → `web-logic-flaw`
- a **SQL/NoSQL injection** in the login field → `web-sqli`/`web-nosqli`
  (the oracle is the injection, not the existence differential)
- an **open registration** that is itself the bug → `web-logic-flaw`/
  `web-mass-assignment` (a `role` param), not existence-oracle
- **pure brute-force with no differential** — if every channel is uniform,
  there is no enum oracle; the credential attack is `web-auth-session`
  unbounded only if the throttle is also absent

## The chain-position precondition

This class produces the INPUT to another class's exploit — a confirmed
account name. It is never the last step; a confirmed name routes to
`web-auth-session`/`web-idor`/`web-oauth-sso`/`web-logic-flaw`.

## The authorization precondition

- **oracle measurement** — the 3-request differential — is a read-only
  probe, in-scope on any authorized target
- **a candidate list** — bounded, on an owned/lab/explicitly-scoped
  target only; never a mass spray on a shared/victim target
- **a lockout probe** — use your OWN known-good account; never lock a
  victim account you do not control to prove the lock exists
- **a throttle bypass** — measuring `X-Forwarded-For` reset is a probe;
  using it to run an unbounded spray is the abuse the control stops —
  record the bypass as the finding, do not run the spray

## The tooling precondition

- `enum_probe.py` — `python3 tools/web/enum_probe.py --selftest` passes
- a known-good name is available (register one if needed)
- `curl -w '%{time_total}'` for the timing channel
