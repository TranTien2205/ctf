# Theory deep — the OAuth trust model, with the full mechanics

The theory module names the concepts. This module carries the full
mechanics — why OAuth works, where the trust breaks, and what the exploit
shapes are.

## The trust model

OAuth 2.0 is a delegation protocol — the app delegates identity to the IdP.
The trust model is a chain:

```
user → browser → app → IdP → app → session
```

Every link in the chain is a trust boundary. The exploit is a break in one
of the links — the app trusts the IdP, the IdP trusts the app, the app
trusts the browser, the browser trusts the cookie.

## The authorization-code flow

```
1. The app redirects to the IdP:
   GET /authorize?client_id=APP&redirect_uri=CALLBACK&response_type=code&state=STATE

2. The IdP authenticates the user and issues a code:
   302 → CALLBACK?code=CODE&state=STATE

3. The app exchanges the code for a token:
   POST /token {grant_type=authorization_code, code=CODE, client_id=APP,
                client_secret=SECRET, redirect_uri=CALLBACK}

4. The IdP issues a token:
   200 {access_token: TOKEN, token_type: Bearer, expires_in: 3600}

5. The app issues a session:
   Set-Cookie: session=SESSION
```

The trust breaks:

- `state` not bound to session → the code is replayable against a different
  session.
- `redirect_uri` not validated → the code is delivered to an attacker URI.
- `code` not bound to `client_id` → a code minted for one client works on
  another.
- `state` not bound to `nonce` → a replayed `id_token` is accepted.

## The implicit flow

```
1. The app redirects to the IdP:
   GET /authorize?client_id=APP&redirect_uri=CALLBACK&response_type=token&state=STATE

2. The IdP issues a token directly:
   302 → CALLBACK#access_token=TOKEN&token_type=Bearer&expires_in=3600

3. The callback page reads the fragment:
   const token = window.location.hash.match(/access_token=([^&]+)/)[1];
```

The trust breaks:

- `response_type` not allowlisted → the implicit flow is accepted.
- The token is in the fragment → leaked via `Referer`, browser history, or
  DOM access.
- The token is bound to `client_id` but not to the request → replayable.

## The OIDC flow

OIDC adds an `id_token` — a JWT carrying the identity:

```
1. The authorize request adds scope=openid:
   GET /authorize?client_id=APP&redirect_uri=CALLBACK&response_type=code&
       scope=openid&state=STATE&nonce=NONCE

2. The token response adds an id_token:
   200 {access_token: TOKEN, id_token: JWT, token_type: Bearer, expires_in: 3600}

3. The id_token carries the identity:
   {sub: USER_ID, email: EMAIL, nonce: NONCE, aud: APP, iss: IDP, exp: EXPIRY}
```

The trust breaks:

- `signature` not verified → the `id_token` is forgeable.
- `alg=none` accepted → the `id_token` is unsigned.
- `aud` not verified → the `id_token` is for a different client.
- `iss` not verified → the `id_token` is from a different IdP.
- `nonce` not bound to the request → the `id_token` is replayable.
- `email`/`preferred_username` used for linking → the pre-registration
  race lands on the attacker's account.

## The PKCE flow

PKCE binds the code exchange to the same client that started the flow:

```
1. The client generates a code_verifier and a code_challenge:
   verifier = random(43..128 chars)
   challenge = BASE64URL(SHA256(verifier))

2. The authorize request carries the challenge:
   GET /authorize?client_id=APP&redirect_uri=CALLBACK&response_type=code&
       code_challenge=CHALLENGE&code_challenge_method=S256&state=STATE

3. The token exchange carries the verifier:
   POST /token {grant_type=authorization_code, code=CODE, client_id=APP,
                code_verifier=VERIFIER}
```

The trust breaks:

- `code_challenge` not required → the PKCE shape is dead.
- `code_challenge_method=plain` accepted → the verifier is in the clear.
- `code_verifier` not re-validated on exchange → a stolen code is
  exchangeable with a wrong verifier.

## The cookie model

The app's session is issued on `Set-Cookie: session=...`; the IdP's token
is issued on `Set-Cookie: token=...`. The trust breaks:

- `SameSite` missing or `None` → a cross-site write lands.
- `HttpOnly` missing → the cookie is readable by JS.
- `Secure` missing → the cookie is sent over plain HTTP.
- `Domain` set to parent → the cookie is shared across subdomains.
- `Path` set to `/` → the cookie is readable everywhere.

Two cookies in the same jar — the app's `session` and the IdP's `token` —
is the swap signal. When the token is overwritten cross-site and the app's
`loginSSO` reads the jar's token, the session becomes the attacker's account.

## The linking model

The app links the IdP's identity to a local account. The linking field is
the trust boundary:

| Field | The trust | The break |
|---|---|---|
| `sub` | the IdP's stable subject | user-controlled `sub` → the race is live |
| `email` | the email claim | `email_verified` not enforced → the race is live |
| `preferred_username` | the username claim | not bound to `sub` → the race is live |
| `groups`/`roles` | the permission claims | broader claims → the scope is broader |

The pre-registration race: the attacker registers the account the bot is
about to register, with their own password. When the linking is on `email`
or `preferred_username`, the OAuth login lands on the attacker's account —
the flag is submitted into the attacker's owned account.

## The trust breaks

| Break | The shape | The falsifier |
|---|---|---|
| `state` not bound to session | code interception | `state` bound to session |
| `redirect_uri` not validated | code interception | `redirect_uri` exact match |
| `SameSite` missing | cookie swap | `SameSite=Lax|Strict` |
| `loginSSO` reads jar token | cookie swap | `loginSSO` reads credentials |
| `linking` on `email`/`username` | pre-registration race | linking on `sub` |
| `response_type` not allowlisted | implicit leak | `response_type` code-only |
| `code_challenge` not required | PKCE bypass | `code_challenge` required |
| `code` not bound to `client_id` | cross-client | `client_id` bound + `aud` verified |
| `signature` not verified | `id_token` forge | signature verified |
| `registration` not idempotent | pre-registration race | registration idempotent |
