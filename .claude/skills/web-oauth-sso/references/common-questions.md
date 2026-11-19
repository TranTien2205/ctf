# Common questions — the OAuth decisions that come up

## Q: I have a `state` in the URL but the app does not seem to validate it. Is this a bug?

Test it: replay the callback with a `state` the session never stored. If the
session is established, `state` is not bound — the CSRF shape is live. If it
is rejected with a `400` naming the mismatch, `state` is bound — the shape
is dead.

## Q: The `redirect_uri` is validated, but loosely. What does that buy me?

A loosely validated `redirect_uri` delivers the code to an attacker-controlled
endpoint. The code can then be replayed against the app's own callback, or
exchanged directly if the `client_secret` is known. The exchange usually
re-validates `redirect_uri` — so the interception only works as a replay when
the `redirect_uri` is strict on exchange.

## Q: The app has two cookies — one from the app, one from the IdP. What does that mean?

Two cookies in one jar is the cookie-swap signal. The app delegates identity
to the IdP's token cookie; when the token is overwritten cross-site (via a
`SameSite`-missing cookie), the app's session becomes the attacker's account.

## Q: The `id_token` is a JWT. Can I forge it?

Only if the signature is not verified, or if `alg=none` is accepted, or if
the `aud`/`iss` claims are not validated. Decode it first — the `sub` claim
is the identity; if you can forge the signature or strip it, you can claim
any `sub`.

## Q: The registration endpoint lets me register any account. What does that buy me?

A pre-registration race: register the account the bot is about to register,
with your own password. The bot's OAuth login lands on your account (the
email/username matches), or the bot's registration fails and the flag is
written to an unreadable account.

## Q: The `code` is in the URL. Can I steal it?

A code in the URL leaks via `Referer`, browser history, and logs. But the
exchange requires `client_id` + `client_secret` + the same `redirect_uri`.
Without the secret, the code is only useful as a replay against the app's
callback — which requires the `state` to also be unbound.

## Q: What is the difference between `state` not validated and `state` not bound?

`state` not validated means any `state` is accepted — the callback does not
check it at all. `state` not bound means a `state` from one session is
accepted by another — the callback checks it, but against the wrong session's
stored value.

## Q: The IdP accepts `response_type=token`. What does that buy me?

Implicit flow — the token is in the fragment. The fragment leaks via
`Referer` on subresource requests, via browser history, and via DOM access.
A token in the fragment is a token that leaks.

## Q: The app accepts `code_challenge_method=plain`. What does that buy me?

`plain` sends the `code_verifier` in the clear — equivalent to no PKCE. A
code minted with a `plain` challenge is exchangeable by anyone who saw the
authorize request.

## Q: The bot visits user-supplied URLs. What does that buy me?

The delivery channel for the cookie swap: a `data:text/html` URL carrying a
form that POSTs to the IdP's login endpoint, overwriting the shared jar's
SSO token. The bot's `loginSSO` step then uses your token.

## Q: The `scope` in the token is broader than what the app requested. What does that buy me?

A broader scope means the token carries more permissions than the app
expected — an `admin` scope, a `read:write` scope, a `offline_access`
refresh token. Check what the broader scope unlocks on the app's endpoints.

## Q: The app uses a custom IdP. What is different?

A custom IdP deviates from the RFC: `state` may not be echoed back,
`redirect_uri` may be validated against a stored list rather than the
request's, `code` may not be bound to `client_id`. Walk the flow once and
name each deviation — the deviations are the attack surface.

## Q: When do I stop?

When the falsifier holds for every shape: `state` bound to session,
`redirect_uri` exact match, `SameSite=Lax|Strict` on the SSO token,
`response_type` code-only, PKCE required, code bound to `client_id`,
`aud` verified, `scope` allowlisted, linking on `sub` + `email_verified`.
When all falsifiers hold, the OAuth surface is closed — reclassify.
