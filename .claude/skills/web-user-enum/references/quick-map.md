# Quick map — the one-screen reference

## The pass, in order

```
1. inventory  every account endpoint (form-surface.md)
2. per form   three arms: KNOWN vs FAKE vs FAKE2
3. channels   body → status+loc → timing → side (channels.md)
4. direct     check-username / REST users / GraphQL / register / reset
5. throttle   15-req burst → absent/at-N → bypass probe
6. names      seeded list through confirmed oracle → verified names
7. record     every cell oracle/uniform; every name + its oracle
8. route      confirmed name → neighbor class; throttle → web-auth
```

## The oracle channels

| Channel | Signal | File |
|---|---|---|
| body | `"no such"`/`code`/class/`data-`/hidden/comment | `channel-body.md` |
| status+loc | `404`/`302`/`?e=`/`?error=` param | `channel-status.md` |
| timing | bcrypt gap 50-300ms; variance | `timing-oracle.md` |
| side | `Set-Cookie`/send/lock/`attempts_remaining` | `channel-side.md` |
| direct | `check`/`available`/`users/{id}`/`userByEmail` | `api-enum.md` |
| register | `"taken"`/`409` — built to reveal | `register-reset-enum.md` |
| reset | `{"emails"}`/send/redirect — send-side | `register-reset-enum.md` |
| graphql | `userByEmail`/`checkUser`/typed `login` err | `api-enum.md` |

## The throttle verdicts

| Result | Meaning |
|---|---|
| no `429`/`423` in 15 | absent — unbounded loop |
| `429`/`423` at N | threshold — record N |
| `X-Forwarded-For`/fresh resets | bypassed — the key trusts input |
| a CAPTCHA after N | challenge control |
| `1/sec` window | a bound, not a block |

## The three-arm rule

`KNOWN` vs `FAKE` proves the oracle; `FAKE` vs `FAKE2` proves it is the
username-class not noise. A single or unmasked response is a candidate,
never a verdict.

## The route table

| Confirmed | Route |
|---|---|
| `admin`/`service`/`flag` + weak pw | `web-auth-session` |
| a reset-token/host-header leak | `web-auth-session`/`web-host-header` |
| a `/api/users/{id}` 200 read | `web-idor` |
| an unlinked email + SSO | `web-oauth-sso` |
| a no-throttle/bypass | `web-auth-session` (the spray) |
| an injection-shaped name diff | `web-sqli`/`web-nosqli`/`web-ssti` |
| a `role`/`is_admin` bound param | `web-mass-assignment` |
