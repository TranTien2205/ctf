# MFA, OTP and account-state enumeration — the richer oracles

## The MFA/OTP send-side

`POST /send-otp`/`/mfa`/`/2fa` — does the code send only for a real row?

```bash
curl -i -X POST -d "user=$KNOWN" "$BASE/send-otp" > og
curl -i -X POST -d "user=$FAKE"  "$BASE/send-otp" > ob
diff og ob; grep -oiE '(sent|otp|code|exist|user|if)[^,}<"]*' og ob
```

- `{"otp_sent":true}` for real, `false`/`null`/error for fake
- a `200` + send vs a `404`/`"no such user"`
- the SEND itself — an SMS/email that fires only for a real row
- a `429`/OTP-specific throttle — the send is a stronger throttle signal

## The verify-OTP oracle

`POST /verify-otp` — `"no pending OTP for user"` vs `"wrong code"` —
the pending-state is a real-row property:

```bash
curl -s -X POST -d "user=$KNOWN&code=000000" "$BASE/verify-otp"
curl -s -X POST -d "user=$FAKE&code=000000"  "$BASE/verify-otp"
# -> "invalid code" (a pending OTP exists) vs "no such user"/"no pending"
```

## The account-state oracles — richer than binary

A real account carries a STATE a fake cannot:

| State | The message | Reveals |
|---|---|---|
| active | `"wrong password"` | exists + active |
| locked | `"account is locked"` | exists + locked |
| pending | `"please verify your email"` | exists + unverified |
| disabled | `"account disabled"`/`"banned"` | exists + deactivated |
| expired | `"password expired"` | exists + needs reset |
| deleted | `"account deleted"`/`410` | existed |
| nonexistent | `"invalid credentials"`/`"no such"` | does not exist |

Three+ distinct responses = a multi-bit oracle — existence AND state.

## The reactivate/confirm/unlock oracles

- `POST /reactivate` — `"sent reactivation"` vs `"no account"`
- `POST /confirm-email` — `"already confirmed"` vs `"no account"`
- `POST /unlock` — `"unlocked"` vs `"no locked account"`
- `POST /resend-verification` — the send fires only for a real pending
- `POST /invite-accept` — `"invite used"`/`"invalid"` vs `"no account"`

Each is a state-aware exists-oracle — `per-endpoint-catalogue.md`.

## The invite/waitlist oracle

`POST /invite`/`/waitlist`/`/request-access` — `"email already invited"`/
`"already registered"` leaks an existing account or a prior invite —
an email-existence oracle outside the auth path.

## The state-timing oracle

A `locked`/`pending` account skips the password check → a DIFFERENT
timing than a real-active account (which hashes) and than a fake (which
returns early) — three timing bands:

```
real-active: lookup + verify       -> ~100-300ms
real-locked: lookup + lock-return  -> ~5ms
fake:        lookup + miss-return  -> ~5ms (or a dummy-hash -> ~hash)
```

A `locked`/`pending` real account is a TIMING-tri-state oracle.

## The state boundary

- `web-user-enum` — the state-message/send/lock exists+state oracle
- `web-auth-session` — the MFA-bypass/OTP-replay/session after
- `web-logic-flaw` — a state-transition bug (skip a step, replay)

The enum measures `exists`+`state`; the exploit is the neighbor's.
