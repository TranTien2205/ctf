# Flow abuse — the canonical attack shapes

The OAuth flow is a sequence of redirects, each carrying parameters the next
step trusts. The attack shapes are named after which step's trust is broken.

## The CSRF shape — state not bound to session

The attacker starts an OAuth flow, captures the `authorize` URL, and has the
victim visit it. The victim's IdP session is active; the flow completes and
the victim's local session lands on the attacker's account — or the victim's
OAuth identity is linked to the attacker's local account.

```bash
# attacker captures the authorize URL
AUTH_URL=$(curl -si "$BASE/login" | grep -oP 'Location: \K.*')
# victim visits it — the callback lands on the victim's app session
# but the OAuth identity is the attacker's
```

**Falsifier**: `state` is a random value stored in the session cookie before
the redirect; the callback rejects a state that does not match.

## The redirect shape — code delivered to attacker

`redirect_uri` is loosely validated, so the code is sent to an
attacker-controlled endpoint. The attacker replays the code against the app's
own callback to hijack the flow, or exchanges it directly (if `client_secret`
is known).

**Falsifier**: `redirect_uri` is an exact match against a registered allowlist,
and the token exchange re-validates the same URI.

## The linking shape — the identity-match field

The app links the OAuth identity to a local account on `email` or `username`.
The attacker registers the same email/username first; the OAuth login lands
on their account. Or: the attacker links their own OAuth identity to the
victim's local account via the CSRF shape.

**Falsifier**: linking is on `sub` (the IdP's stable subject), `email` is only
used when `email_verified: true`, and linking requires an authenticated step.

## The swap shape — the shared cookie jar

Two cookies — app session and IdP token — in one jar. A cross-site write (the
text/plain JSON trick) overwrites the IdP token; the app's `loginSSO` step
ignores credentials and uses the jar's token. The app's session becomes the
attacker's account.

**Falsifier**: the SSO token cookie has `SameSite=Lax` or `Strict`, or the
login endpoint enforces `Content-Type: application/json` strictly.

## The implicit shape — token in the fragment

`response_type=token` or `id_token` puts the token in the URL fragment. The
fragment is not sent to the server, but it is in the browser history, in the
`Referer` header of subresource requests, and in DOM access. A token in the
fragment is a token that leaks.

```bash
# check whether the app accepts implicit flow
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=token&state=XYZ&nonce=N"
# if it 302s to https://app/callback#access_token=..., the fragment is live
```

**Falsifier**: `response_type` is allowlisted to `code` only.

## The PKCE shape — no code challenge

PKCE binds the code exchange to the same client that started the flow. Without
it, a stolen code is exchangeable by anyone who has the `client_secret`.

```bash
# check whether PKCE is enforced
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
# if the authorize request has no code_challenge, PKCE is not enforced
```

**Falsifier**: `code_challenge` is required and `code_challenge_method` is
`S256` (not `plain`).

## The scope shape — broader than requested

The app requests `scope=openid` but the IdP grants `scope=openid profile email`
— or the app accepts a broader scope in the authorize request. The access
token carries more claims than the app expected.

**Falsifier**: `scope` is allowlisted and the IdP grants only what was
requested.

## The nonce shape — replayed callback

`nonce` binds the `id_token` to the authorize request. Without it, a captured
`id_token` is replayable.

**Falsifier**: `nonce` is required and validated on the callback.

## The multi-client shape — code cross-client

The code is bound to `client_id` at issuance. If the app has a second
registered client with a different `client_secret`, a code minted for client
A can be exchanged by client B.

**Falsifier**: the code is bound to `client_id` and the token endpoint rejects
a different client.

## The ordering

Walk the flow once. Name the trust that is broken at each step. The cheapest
shape is usually `state` not bound to session — test it first. Then
`redirect_uri` validation. Then account linking. Then the cookie-swap
preconditions.
