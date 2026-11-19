# Mechanism — what a user-enumeration oracle is

## The core asymmetry

An authentication system handles a real account and a nonexistent one
*differently*. Somewhere in the code there is a branch:

```
user = db.lookup(username)
if user is None:
    return "no such account"          # or silently skip hashing
else:
    if verify(password, user.hash):   # the expensive path
        return success
    return "wrong password"
```

Two things differ between the arms:

1. **The message or artifact** the app emits (the text, the redirect, the
   status, a cookie, a JSON boolean).
2. **The work the app does** — the `verify(password, user.hash)` call runs
   only for real users. A bcrypt/argon2/scrypt hash costs 50-500ms; the
   `user is None` arm returns in ~1ms. The work asymmetry is a **timing
   oracle**.

Every enumeration primitive is a measurement of one of these two
differences.

## The oracle contract

An enumeration oracle is a pair of requests that differ ONLY in the
username, measured on the SAME endpoint with the SAME other fields:

```
R(known_user, password)   -> response_A
R(random_user, password)  -> response_B
```

If `response_A != response_B` on any channel (text / status / redirect /
timing / cookie / embedded boolean), and the difference repeats, the
endpoint enumerates accounts.

## The three request shapes

- **known-good** — a username that exists (yours, a seeded account,
  `admin`, a name the app leaked)
- **known-bad** — a username that provably does not (`zzz-` + random, a
  64-char random string)
- **repeated-bad** — the same bad name again, to confirm the signal is a
  property of the username, not request noise

## Why it is a class, not a technique

The oracle is not the exploit — the exploit is what a confirmed account
list buys: a credential-stuffing target, a reset-flow target, a weak
password on a known account, a second factor worth bypassing. The enum
is the first link; the chain lives in `web-auth-session`.

## Throttling — the class's other half

The class is "User enumeration / auth throttling" because the same
endpoint carries the second question: does the app bound the guessing
loop? A missing throttle is itself a finding; a throttle that a header
(`X-Forwarded-For`) resets is a bypass finding.
