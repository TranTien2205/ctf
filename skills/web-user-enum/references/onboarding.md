# Onboarding — the 60-second orientation

## The one-line idea

Ask an auth endpoint "is this account real?" by comparing what it does
for a real username vs a fake one — the difference is the oracle.

## The 30-second probe

```bash
# 3 requests, same form, only the username changes
curl -i -X POST -d 'user=admin&pass=x'        "$BASE/login"
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x'   "$BASE/login"
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x'   "$BASE/login"   # repeat
```

Look at: the response TEXT, the status code, the `Location` redirect,
how long it took, and any `Set-Cookie`.

## Where it differs

- a login that says `"no such user"` vs `"wrong password"`
- a register that says `"username taken"`
- a reset that sends a link only to a real account
- a login that is SLOWER for a real account (the password-hash runs)
- an endpoint that returns `{"available":false}` for a taken name

## The two questions this class answers

1. **Does the endpoint reveal which accounts exist?** (the oracle)
2. **Can the guessing loop run unbounded?** (the throttle — or its bypass)

## What to do with a confirmed account

A real username is a target — feed it to `web-auth-session` (a weak
password, a reset bug, a spray), `web-idor` (read its object), or
`web-oauth-sso` (an email collision).

## The one rule

Prove the oracle with 3 requests — never spray a wordlist to "test" it.
The list is bounded, authorized, and second.
