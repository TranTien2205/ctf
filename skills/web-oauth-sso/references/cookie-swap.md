# Cookie swap — the SSOS verified shape

Two session cookies — one from the application, one from the identity provider
— and a bot that holds them in a shared jar. The exploit lives in the ordering
of cookie writes, not in any single request.

## The shared-jar model

The bot visits a page carrying `Cookie: session=APP_SESSION; token=IDP_TOKEN`.
Both writes land in the same jar. When the app later reads the jar to decide
which account the session belongs to, the *IDP* token is what matters — the
app delegates identity to the provider. Swap the IDP token for one you
control, and the app's session becomes your account.

## The SSOS preconditions

| Precondition | Why it matters |
|---|---|
| `loginSSO` ignores credentials, authorizes using the shared jar's token cookie | the bug is *in the app's own OAuth step* — it trusts the jar, not the credentials |
| JSON binder parses raw body as JSON regardless of `Content-Type` | the cookie swap is delivered by a `text/plain` form — a JSON body without the JSON content type |
| SSO token cookie is `HttpOnly` with **no `SameSite`** | cross-site writes land in the jar |
| registration endpoint lets you pre-register a fixed account | you own the account the bot later tries to register |

## The swap mechanics — the text/plain JSON trick

A `Content-Type: text/plain` form submits `name=value` pairs. Gin's
`ShouldBindJSON` reads the raw body regardless of `Content-Type`. The trick:
name the input field `{"email":"attacker@domain","password":"attacker` and
the value `password"}`. The form body becomes:

```
{"email":"attacker@domain","password":"attacker=password"}
```

which is not valid JSON — but the trick is the *prefix*: the input name is
`{"email":"attacker@domain","password":"attacker_password` (no closing brace)
and the input value is `"}` — the closing quote and brace. Concatenated:

```
{"email":"attacker@domain","password":"attacker_password"}
```

Valid JSON, submitted as `text/plain`, parsed by the JSON binder. The login
succeeds and the IdP's `Set-Cookie` lands in the shared jar, overwriting the
bot's own SSO token.

```html
<form method="POST" action="https://sso.internal/api/login" enctype="text/plain">
  <input name='{"email":"student@domain","password":"attacker_password' value='"}'>
  <input type="submit">
</form>
<script>document.forms[0].submit()</script>
```

## The delivery — the bot's visit-url endpoint

The bot visits user-supplied URLs. A `data:text/html,...` URL carries the
form inline; the bot's shared jar already holds the app session. The form
POSTs to the IdP's login endpoint, the Set-Cookie overwrites the SSO token,
and the bot's next `loginSSO` step uses your token — your account.

## The detection shape

- The app sets a session cookie *and* delegates identity to an SSO token
  cookie — two cookies, one jar.
- The SSO token cookie has `HttpOnly` but **no `SameSite`** — cross-site
  writes land.
- The OAuth login endpoint accepts `text/plain` or `application/x-www-form-urlencoded`
  bodies that a JSON binder reads as JSON.
- The bot's visit-url endpoint renders user-supplied URLs — the delivery
  channel.

## Falsifier

The SSO token cookie has `SameSite=Lax` or `Strict` (cross-site writes are
rejected), or the login endpoint enforces `Content-Type: application/json`
strictly (the text/plain trick fails), or the app binds the OAuth identity
to `sub` rather than to the jar's token. When this holds, the swap surface
closes — move to state or redirect_uri.
