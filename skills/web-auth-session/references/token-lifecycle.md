# Token lifecycle — issuance, rotation, expiry, revocation, storage

The full arc: how a token is born, how it's used, how it dies, and where
each stage leaks.

---

## 1. Issuance

The moment a credential becomes a token. The leaks:

- **Logged** in the access log as a query param (`?token=`).
- **Cached** in the response (`Set-Cookie` + `Cache-Control: public` or
  absent on a shared cache).
- **In the body** of a JSON response — readable by XSS if not also
  `HttpOnly`-cookied.
- **In `Set-Cookie` on a GET** — `Referer` to external resources.
- **Reflected** in the response (login form re-renders the creds).
- **In the URL** of a redirect (`Location: /home?token=T`).
- **In the `id_token`/`access_token` fragment** — `#access_token=` is
  browser-readable.
- **In an `Authorization` header on a 302** — the client forwards it
  cross-origin if the client doesn't strip it.
- **In `Set-Cookie` with a too-broad `Domain`** — sibling subdomains
  read it.
- **In `document.cookie`** — readable to JS.
- **In `localStorage`/`sessionStorage`** — readable to JS and every
  future XSS.
- **In `window.name`/`postMessage`** — cross-window leaks.
- **In a `service worker`** — the token is cached for offline.
- **In a `SharedWorker`/`BroadcastChannel`** — cross-tab.
- **In `performance.getEntries()`** — if a request carried the token in
  the URL.

## 2. Storage

Where the client holds it. Each has a different threat:

| Store | XSS can read | CSRF can trigger | Network sniff | Persistence |
|---|---|---|---|---|
| `HttpOnly` cookie | no | yes | if no `Secure` | `Max-Age`/`Expires` |
| `Secure` cookie | no | yes | no | same |
| `SameSite=Strict` cookie | no | no (strict) | same | same |
| `SameSite=Lax` cookie | no | GET-only | same | same |
| `SameSite=None` cookie | no | yes | needs `Secure` | same |
| `localStorage` | yes | no | no | persistent |
| `sessionStorage` | yes | no | no | tab lifetime |
| `document.cookie` | yes | yes | no | whatever's set |
| `window.name` | yes | no | no | window lifetime |
| `IndexedDB` | yes | no | no | persistent |
| `Cache`/`CacheStorage` | yes | no | no | persistent |
| `serviceWorker` | yes | no | no | persistent |
| `SharedWorker` | yes | no | no | process lifetime |
| `BroadcastChannel` | yes | no | no | while open |
| `Authorization` header (manual) | yes | no | if no TLS | request lifetime |
| `URL` fragment | no (server) | no | no (server doesn't see) | URL lifetime |
| `URL` query | server sees | yes | logs | URL lifetime |
| `Set-Cookie` (as data) | yes | yes | yes | whatever's set |
| `WWW-Authenticate` | no | no | no | n/a |
| `?access_token=` | yes | yes | logs | URL lifetime |
| `#access_token=` | yes | no | no | URL lifetime |
| `X-Auth-Token` header | yes | no | if no TLS | request lifetime |
| `X-API-Key` header | yes | no | if no TLS | request lifetime |

## 3. Rotation

When the credential should change and doesn't:

- **On login**: the session id MUST change. If the pre-login sid == the
  post-login sid → fixation.
- **On privilege change**: escalate → rotate. Otherwise a stale
  pre-escalation session may have different binding.
- **On password change**: all sessions MUST die. Otherwise the attacker
  keeps theirs.
- **On logout**: the sid MUST die server-side.
- **On remember-me use**: the validator SHOULD rotate per use.
- **On OAuth re-auth**: the `code`/`token` MUST be single-use.

The test is always two-device: capture the credential at T1, change
state at T2, replay at T3.

## 4. Expiry

- `exp`/`iat`/`nbf`/`jti` on JWTs.
- `Max-Age`/`Expires` on cookies.
- `expires_at` in the session row.
- `iat`+idle-timeout on server-side sessions.
- `refresh_token` expiry separate from `access_token`.
- `code` expiry (OAuth — usually seconds).
- `state` expiry (OAuth CSRF protection).
- `nonce` expiry (OIDC replay protection).
- `reset_token` expiry (password reset — usually minutes).
- `magic_link` expiry.
- `mfa_ticket` expiry.
- `backup_code` — single-use by definition.
- `device_trust_token` — days to months.
- `impersonation_token` — should be minutes, often hours.

**The bugs**: no `exp` at all, `exp` ignored, `exp` only on one token
type, `exp` clock-skew accepted too loosely, `Max-Age` present but
session row never cleaned, `exp` refreshed on every use (never dies).

## 5. Revocation

How a credential is killed:

- **Blacklisted `jti`** — the token's `jti` is stored; verify consults
  the list.
- **Session deletion** — the DB row deleted on logout.
- **Key rotation** — all tokens signed with old key die.
- **"Increment `user.session_version`"** — every token carries
  `session_version`; bump it → all old die.
- **"Set `user.logged_out_at`"** — `iat` before that is dead.
- **PKCE `code_verifier`** — binding kills replay.

**The bugs**:

- `jti` checked but the list is in-memory → restart clears it.
- `jti` never checked → revocation doesn't exist.
- `session_version` checked but the claim isn't signed → forge it.
- The session row is `DELETE`'d on logout but `GET /session` re-creates
  it lazily → replay.
- `access_token` revoked but `refresh_token` survives → refresh to a new
  access token.
- Key rotation is manual → the old key works until someone notices.
- "Soft-delete" the session row (`deleted_at`) but the lookup doesn't
  filter it → replay.
- A session "deactivates" but a background worker/job still uses it.

## 6. The replay tests

| Test | How | Expected |
|---|---|---|
| post-logout replay | login → logout → replay sid | 401/403 |
| post-password-change | login → change password → replay sid | 401/403 |
| post-escalation | login → escalate role → replay sid | either works (if rotate) or fails (if not) |
| post-rotation | login → refresh → replay old sid | 401 |
| post-revocation | login → `DELETE /session` → replay | 401 |
| post-key-rotation | mint token → rotate keys → replay | 401 |
| concurrent sessions | login twice, replay both | depends — count |
| `jti` replay | send same token twice | 401 second time (if `jti` checked) |
| `exp` boundary | send at `exp-1`, `exp`, `exp+1` | 401 at `exp` |
| clock-skew | send `exp+30s` | depends on skew tolerance |

## 7. The session-fixation deep-dive

```
attacker: GET / → Set-Cookie: sid=ATTACKER
attacker: sends victim link https://t/login?sid=ATTACKER
victim:  GET /login?sid=ATTACKER → Set-Cookie: sid=ATTACKER (app reuses)
victim:  POST /login → session bound to ATTACKER
attacker: Cookie: sid=ATTACKER → victim's session
```

The tell: `Set-Cookie` on `GET /login` AND the app reuses a
client-supplied `sid` instead of minting fresh.

## 8. The "two sessions, one account" test

```
device 1: login as A → sid_1
device 2: login as A → sid_2
replay sid_1, sid_2 on /me
```

- Both work → concurrent sessions allowed (fine if documented).
- sid_1 dies on sid_2's login → single-session (fine).
- sid_1 still works after sid_2's login → concurrent + no notification.
- sid_1 works but shows sid_2's data → session confusion.
- Either sid works for *any* user → catastrophic.

## 9. The refresh-token rules

- `refresh_token` SHOULD be `HttpOnly` cookie or returned only on
  `/token` POST, never in URL.
- `refresh_token` SHOULD rotate per use (the old one dies).
- `refresh_token` SHOULD be bound to `client_id` and `redirect_uri`.
- `refresh_token` SHOULD be revocable separately.
- `refresh_token` should NOT be readable by JS.
- `refresh_token` expiry should be bounded (days, not years).

## 10. The "one-session-per-thing" patterns

- **Per-device**: `sid` + `device_id` — replay from another device fails.
- **Per-IP**: `sid` + `remote_addr` — replay from another IP fails.
- **Per-UA**: `sid` + UA hash — replay from another browser fails.
- **Per-context**: `sid` bound to `scope`/`aud` — another aud rejects.
- **Per-user**: `sid` bound to `user_id` — only that user resolves.
- **Per-purpose**: `reset_token` works only on `/reset`, not `/login`.

The test for each: replay the credential in a *different* context and
see if it dies.
