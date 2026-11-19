# Multi-step chains — enum as the first link

## Chain: enum → credential stuffing → session

```
a confirmed oracle (login/register/reset)
  -> a candidate list, bounded by the throttle measurement
  -> spray one common password across confirmed accounts
  -> a valid credential -> web-auth-session
```

## Chain: enum → reset-flow → account takeover

```
a confirmed account (e.g. admin)
  -> the reset endpoint's oracle confirms it exists
  -> a predictable/leakable reset token (web-auth-session, web-logic-flaw)
  -> reset the password -> log in -> the account's data/flag
```

## Chain: enum → IDOR → account read

```
a confirmed username
  -> /api/users/{name} or /users/{id} returns the object (web-idor)
  -> read the account's email/role/data -> a wider pivot
```

## Chain: enum → SSO email-collision → pre-hijack

```
a confirmed victim email
  -> register it yourself / an SSO provider auto-links on email match
    (web-oauth-sso)
  -> the victim's account links to your SSO identity
```

## Chain: enum → weak/default password → flag

```
a confirmed service/admin account
  -> a weak or default password (admin:admin, service:service)
  -> a session -> the flag on the account's page
```

## Chain: enum → MFA-bypass → session

```
a confirmed account + its password (weak/stuffed)
  -> the MFA step -> a guessable/unthrottled OTP or a replay
    (web-auth-session)
  -> a full session
```

## Chain: no-throttle → brute force → session

```
a missing rate limit proven (15+ reqs, no 429/lock)
  -> a bounded credential brute force on a confirmed account
  -> a session -> web-auth-session
```

## Chain: throttle-bypass → unbounded spray

```
a per-IP limit + an X-Forwarded-For reset
  -> the counter never fires
  -> an unbounded password spray across the enum'd accounts
```

## The enum's position

The enum is always link 1 — it produces the account names the chain
acts on. Its budget ends at "a verified account name + the channel
that confirmed it"; every next step is the routed class.
