# Detection surface (deep) — the auth surface's full oracle topology

## The complete surface tree

```
the app
├── HTML forms
│   ├── /login            — text/status/timing/side/lock
│   ├── /register         — taken/409/timing
│   ├── /forgot-password  — send-side/timing/field
│   ├── /forgot-username  — sent-side
│   ├── /unlock|/reactivate — unlocked vs no-locked
│   ├── /mfa|/2fa|/send-otp — code-sent/timing
│   └── /invite|/contact  — already-member
├── API
│   ├── /api/login|/auth|/token|/oauth — JSON error/boolean/status
│   ├── /api/check-username|/available|/user-exists — direct bool
│   ├── /api/users/{id|name} — 200/404 + web-idor
│   └── /api/register|/reset — API variants
├── GraphQL
│   ├── query{userByEmail} — null vs object
│   ├── query{checkUser|userExists} — direct bool
│   └── mutation{login} — typed error code
├── SSO/federated
│   ├── /oauth/token — invalid_grant vs invalid_client
│   ├── Sign-in-with-X — account_not_found on unlinked
│   └── /saml — external vs local redirect
└── other
    ├── basic-auth — realm/message diff
    ├── ws:// auth frame — typed auth_error
    └── LDAP-backed bind — typed bind error
```

## The cheapest-leak ordering (the real path)

```
check-username (direct, unauth)
  > register-taken (built to reveal)
    > forgot-username/unlock (often forgotten)
      > reset (send-side)
        > api/graphql (typed errors)
          > login (most hardened)
            > mfa (least attacked)
```

## The per-surface coverage matrix

A surface is closed only when every endpoint ON it is measured; an
endpoint is closed only when every channel ON it is measured. The full
coverage is `per-endpoint.md` × `per-channel.md` — a `/login` uniform
on body+status but unmeasured on timing is still open.

## The hidden surface

- a `/check-username` AJAX the register page makes — grep the bundle
- a `/api/internal/` endpoint — `web-source-map` recovered it
- a `/graphql` introspection that names a `checkUser` resolver
- a `v2`/`beta`/`internal` route alias the canonical route lacks
