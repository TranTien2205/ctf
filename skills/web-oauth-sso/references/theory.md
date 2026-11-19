# Theory — why OAuth flows break

OAuth is a delegation protocol: the application delegates identity to an
identity provider. The trust boundaries are the places where the delegation
is established — and each boundary is a place where the wrong party can be
trusted.

## The three parties

| Party | Role | Trust it holds |
|---|---|---|
| User agent | the browser | carries the redirects, the cookies, the fragments |
| Client | the application | holds the `client_secret`, establishes the session |
| Authorization server | the IdP | mints the code, the token, the `id_token` |

The user agent is the untrusted middle: it carries everything, and it is
controlled by whoever's browser it is. The client trusts the user agent to
carry the `state` faithfully; the IdP trusts the client to validate the
`redirect_uri`; the client trusts the IdP to verify the `code` was issued
for the right `redirect_uri`.

## The trust boundaries

| Boundary | What is trusted | What goes wrong |
|---|---|---|
| authorize | the user agent carries `client_id`, `redirect_uri`, `state`, `scope` | `redirect_uri` and `state` are attacker-controlled |
| callback | the user agent carries `code` and `state` | `code` is replayable; `state` may not be bound |
| token | the client sends `code`, `client_secret`, `redirect_uri` | `client_secret` may be leaked; `redirect_uri` may not be re-validated |
| userinfo | the client sends `access_token` | the token is a bearer artifact — whoever holds it is trusted |
| session | the client reads the jar | the jar may hold a swapped token |

## The delegation gap

The application delegates identity to the IdP, but it still makes the final
decision: which local account does this OAuth identity map to? That decision
— the account-linking step — is the gap where the delegation is exploited.

- Link on `email` → the attacker registers the same email first.
- Link on `username` → the attacker registers the same username.
- Link on `sub` → the IdP's stable subject, not attacker-controlled. Safer.
- Always create a new account → the OAuth identity is never linked; the
  pre-registered account is orphaned.

## The bearer-token problem

The access token is a bearer artifact: whoever presents it is trusted. It is
not bound to the client's TLS channel, the client's IP, or the client's
`client_secret` beyond the exchange. A token that leaks — via the fragment,
the `Referer`, the logs, the browser history — is a token anyone can use.

## The two-cookie problem

The app sets a session cookie; the IdP sets a token cookie. Both live in the
same jar. The app delegates identity to the IdP's token — so the app's
session is only as strong as the IdP's cookie's `SameSite` attribute. When
`SameSite` is missing or `None`, a cross-site write overwrites the token,
and the app's session becomes the attacker's account.

## The redirect chain problem

`redirect_uri` is a URL the IdP trusts to deliver the code. When the
validation is loose — prefix, suffix, wildcard, substring — the code is
delivered to an endpoint the attacker controls. The open-redirect chain:
`redirect_uri=https://app/callback/../redirect?to=evil` — the IdP's check
passes, the app's open redirect forwards the code.

## The ordering problem

OAuth is a sequence: authorize → callback → token → userinfo → session.
Each step trusts the previous one. The exploit lives in the ordering — a
registration raced before the bot's own registerUser, a cookie swapped
before the `loginSSO` step, a code replayed before the original exchange.
The sequence is the attack surface.
