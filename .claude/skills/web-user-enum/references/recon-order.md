# Recon order — where this class sits in the larger pass

## The enum's position in a web challenge

```
web-triage (what IS this app?)
    |
    v
the account-touching surface found (a login/register/reset/API)
    |
    v
web-source-map (the bundle names the check/api endpoints)
    |
    v
web-user-enum (does an exists-oracle fire? is the loop bounded?)
    |
    +-- a confirmed account name ----> web-auth-session (spray/reset/MFA)
    |                                 web-idor          (the object)
    |                                 web-logic-flaw    (reset-flow)
    |                                 web-oauth-sso     (email-collision)
    +-- a throttle finding -----------> web-auth-session (the credential loop)
    +-- all-uniform ------------------> the neighbor class (session/logic)
```

## When to open this class

- AFTER `web-triage` has named the target as having an auth surface
- AFTER `web-source-map` (if a bundle exists) has named the
  check/api/reset endpoints — the bundle often reveals the
  `check-username` route the rendered page hides
- BEFORE the credential attack — the enum produces the account names
  `web-auth-session` attacks

## When NOT to open it

- a uniform-auth target whose session/token is the bug → `web-auth-session`
- a broken business rule → `web-logic-flaw`
- an injection in the user field → `web-sqli`/`web-nosqli`
- no account-touching endpoint at all → the class does not apply

## The class's output

- a verified account name → the neighbor's input
- a measured throttle (absent/threshold/bypassed) → a finding
- a per-(form×channel) coverage record → the next attempt's kill-map

## The budget position

The enum is a bounded measurement pass (5 probes / 15 min per
mechanism-class budget) — the 3-request oracle, the bounded burst, the
seeded list. The SPRAY/BRUTE-FORCE is a different budget — it is the
neighbor class's credential attack, not this class's oracle.
