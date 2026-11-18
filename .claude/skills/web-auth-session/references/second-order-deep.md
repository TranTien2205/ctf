# Second-order auth — the deferred trust

The first-order auth check is on the request; the second-order is on
the *stored* or *deferred* artifact that a later request trusts. The
forge works on the first hop or the second — sometimes only the second.

---

## 1. The stored claim

A claim written at registration is trusted later:

```
POST /register {username:"admin", role:"user"}   → stores {username:"admin", role:"user"}
POST /profile  {bio:"<xss>"}                     → stored bio
GET  /admin/users                                → renders stored usernames → XSS to admin
```

The stored `username`/`bio`/`avatar`/`email`/`name` is a second-order
sink — it's written in one request, rendered in another. An admin
viewing the user list renders your stored XSS → steal the admin session.

## 2. The queued session

An async job processes a session/token/claim you queued:

```
POST /export  → queues a job with your session
worker reads the job → uses your session → but the worker runs as admin?
```

The job's execution context may differ from the request's — the worker
may run with elevated privilege, or the queued session may be
re-validated against a stale ACL.

## 3. The webhook token

`POST /webhooks {url:"https://you/wh", secret:"s"}` — the app later
POSTs to your URL *signed with its key*. The signature you receive
leaks the signing key → forge other signatures.

## 4. The password-reset that renders the username

`POST /forgot {email:"victim@"}` → the reset email says "Hi <username>"
— the username is your stored XSS payload → the email client renders it
→ steal the token from the reset link's Referer.

## 5. The admin-visit trigger

`POST /report {url:"https://t.tld/profile"}` → an admin bot visits →
the profile carries your stored XSS → steal the bot's admin session.

The first-order is `POST /report` (any user can); the second-order is
the admin's *session* that visits — your stored payload executes in it.

## 6. The session-fixation-into-privilege

```
GET /login?sid=EVIL → plant sid=EVIL on admin-bot's browser
admin-bot visits /login → gets sid=EVIL → admin-bot logs in → sid=EVIL is now admin
you replay sid=EVIL → admin session
```

The fixation is first-order on the *admin's* browser, second-order on
the session store.

## 7. The token in the audit log

`POST /login` logs `user=X token=Y` to an admin-viewable audit log —
the logged token is a live session → read the log (as admin, or via
another vuln) → replay the logged token.

## 8. The "remember me" into another account

`POST /login {remember:true}` → sets `remember_token` — later,
`GET /` with the cookie auto-logs-in. If the `remember_token` is
predictable or bound to the wrong account, the second-order auto-login
is a session-forge.

## 9. The MFA-device-trust into the future

`POST /mfa {code:X, remember_device:true}` → sets `trusted_device`
cookie. Later logins with the cookie skip MFA. If the `trusted_device`
cookie is forgeable (`md5(user_id)`), the second-order is a permanent
MFA bypass.

## 10. The OAuth account-link race

`POST /oauth/link` binds an external IdP to your account — race the
link request so the same IdP links to two accounts, or link the
victim's IdP to yours.

## 11. The session-fixation via subdomain

`admin.tld` and `attacker.tld` share `.tld` — a cookie planted on
`.tld` from the subdomain reaches the main app. Plant `sid=EVIL;
Domain=.tld` → victim on `admin.tld` gets your sid.

## 12. The "the flag is the next request" shape

The forge gives you a session, but the flag isn't in any endpoint —
it's in the *next* request the *server* makes on your behalf. An
admin's session can trigger an internal fetch (`/admin/fetch?url=`)
that reaches loopback — the second-order is the server's own request.

## 13. The stored JWT

A JWT issued once is stored (in a comment, a post, a file) — later,
another user's view of that comment *sends* the stored JWT → the stored
JWT is replayed → it's a token-swap by storage.

## 14. The "who wins on duplicate" second-order

Two writes with the same key — the second overwrites. If the second
write carries a privileged field (a `role` the first didn't have), the
stored record gains the field. The first write is surface; the second
is the forge.

## 15. The notification-carried token

`POST /notify {to:"admin", msg:"<link>"}` → admin gets a notification
with your link → clicks → the link's Referer/your endpoint logs the
admin's session token.

## 16. The second-order registration

`POST /register` stores `username` — `GET /users` renders it unsanitized
to any viewer. A stored XSS in the username is the second-order payload;
the viewer's session is the steal.

## 17. The OAuth id_token stored and replayed

`POST /oauth/callback` stores the `id_token` — a later `/api/me`
*replays* the stored `id_token` to the API → a stored `id_token` with
elevated claims is the second-order forge.

## 18. The "the session outlives the claim"

You forged `role:user` — but the session was issued *before* your role
was downgraded. Sessions with stale claims persist — an old `role:admin`
session replayed still works until expiry/revocation.

## 19. The audit-trail falsifier

The admin views the audit log — your forged requests are there. If the
log records `user_id` from the session, your forged `user_id:1` shows
as admin's action — a second-order attribution bug.

## 20. The carry-through

The general shape: **the trust you break on hop N is trusted on hop
N+1**. The first-order check is always on the immediate request; the
second-order is on the stored/deferred/queued/notified/rendered
artifact. For every write endpoint, ask *where does this value land
next* — the landing is the second-order surface.
