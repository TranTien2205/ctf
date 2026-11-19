# Preconditions (deep) — the full applicability map

## The applies matrix

| Condition | Verdict |
|---|---|
| an account-touching endpoint exists | applies |
| the question "does X exist?" feeds a chain | applies |
| a uniform-auth target with a session/token bug | `web-auth-session` |
| a broken business rule (not existence) | `web-logic-flaw` |
| an injection in the username field | `web-sqli`/`web-nosqli` |
| a `200`/`404` user-resource read | `web-idor` (+ enum) |
| an SSO email-collision | `web-oauth-sso` (+ enum) |
| no account endpoints at all | does not apply |

## The scope ladder

| Measurement | Scope |
|---|---|
| the 3-request oracle | read-only, in-scope on authorized targets |
| the bounded burst (8-15) | read-only-ish, in-scope |
| a small seeded-name list (10-50) | owned/lab/explicitly-scoped |
| a lockout probe | your OWN account only — never a victim's |
| a throttle-bypass measurement | a probe — record the bypass, do not run the spray |
| a mass wordlist spray | never — the abuse the throttle stops |

## The chain precondition

This class produces the INPUT to a neighbor's exploit — a confirmed
account name or a throttle finding. It is never the terminal step; a
confirmed name routes to `web-auth-session`/`web-idor`/`web-logic-flaw`/
`web-oauth-sso`. If the chain does not need the account list, the enum
measurement still stands as a finding.

## The tooling precondition

- `enum_probe.py` — `--selftest` passes
- a known-good name (register one if needed)
- `curl -w '%{time_total}'` for the timing channel
- a `python3 -c`/`awk` for the median/stdev
- a CSRF-aware fetch if the form requires a token

## The measurement precondition

- a noise baseline (`bad1`==`bad2`) before any good-vs-bad diff
- session affinity for a comparable timing read
- a cache-bust for a cached response
- the format resolved (`admin` vs `admin@x.c`) before the oracle read
