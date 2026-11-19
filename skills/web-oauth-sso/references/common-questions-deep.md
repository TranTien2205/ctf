# Common questions deep — the OAuth decisions with the full mechanics

## Q: I have a `state` in the URL but the app does not seem to validate it. Is this a bug?

Test it — but test it correctly. There are two different bugs:

1. **`state` not validated at all** — the callback accepts any `state`, even
   one the app never issued. Test: `callback?code=ABC&state=RANDOM`.

2. **`state` not bound to the session** — the callback accepts a `state` that
   was issued for a *different* session. Test: capture `state1` from session 1,
   replay it against session 2's callback.

Both are the CSRF shape, but they are different mechanisms. The first means
the app does not check `state` at all; the second means it checks `state`
against the wrong session's stored value.

## Q: The `redirect_uri` is validated, but loosely. What does that buy me?

A loosely validated `redirect_uri` delivers the code to an
attacker-controlled endpoint. But the code exchange still requires
`client_id` + `client_secret` + the same `redirect_uri`. Without the
`client_secret`, the code is only useful as a replay against the app's own
callback — which requires the `state` to also be unbound.

The interception chain:
1. `redirect_uri` is loosely validated → code delivered to `evil.com`.
2. `state` is not bound → the code is replayable against the app's callback.
3. The attacker replays the stolen code against `https://app/callback` →
   session on victim's account.

## Q: The app has two cookies — one from the app, one from the IdP. What does that mean?

Two cookies in one jar is the cookie-swap signal. The app delegates identity
to the IdP's token cookie; when the token is overwritten cross-site, the
app's session becomes the attacker's account.

The preconditions for the swap:
1. The SSO token cookie has `SameSite` missing or `None` — cross-site writes land.
2. The app's `loginSSO` step ignores credentials and uses the jar's token.
3. A cross-site write can overwrite the token — a `text/plain` or form POST
   to the IdP's login endpoint.

## Q: The `id_token` is a JWT. Can I forge it?

Only if the signature is not verified, or if `alg=none` is accepted, or if
the `aud`/`iss` claims are not validated. Decode it first — the `sub` claim
is the identity; if you can forge the signature or strip it, you can claim
any `sub`.

The forge chain:
1. Decode the `id_token` — read the `sub`, `iss`, `aud`, `exp`, `nonce`.
2. Forge a new `id_token` with `alg=none` or a weak signature.
3. Submit it — if the app accepts it, the `id_token` is forgeable.

## Q: The registration endpoint lets me register any account. What does that buy me?

A pre-registration race: register the account the bot is about to register,
with your own password. The bot's OAuth login lands on your account (the
email/username matches), or the bot's registration fails and the flag is
written to an unreadable account.

The race chain:
1. The bot registers a fixed account at startup — `student@domain`.
2. The attacker hammers `POST /api/register` for `student@domain` with their
   own password — before the bot's `registerUser` step runs.
3. The bot's registration fails; its OAuth login lands on the attacker's
   account.
4. The flag is submitted into the attacker's owned account.

## Q: The `code` is in the URL. Can I steal it?

A code in the URL leaks via `Referer`, browser history, and logs. But the
exchange requires `client_id` + `client_secret` + the same `redirect_uri`.
Without the secret, the code is only useful as a replay against the app's
callback — which requires the `state` to also be unbound.

The steal chain:
1. The code is in the URL — `https://app/callback?code=ABC&state=XYZ`.
2. The code leaks via `Referer` on a subresource the callback page loads.
3. The attacker replays the stolen code against `https://app/callback` —
   but `state` must also be unbound, or the `redirect_uri` must not be
   re-validated on exchange.

## Q: What is the difference between `state` not validated and `state` not bound?

`state` not validated means any `state` is accepted — the callback does not
check it at all. `state` not bound means a `state` from one session is
accepted by another — the callback checks it, but against the wrong session's
stored value.

The distinction matters for the exploit: `state` not validated means a
random `state` works — the attacker does not need to know the victim's `state`.
`state` not bound means the attacker needs a `state` that was issued for a
session — their own.

## Q: The IdP accepts `response_type=token`. What does that buy me?

Implicit flow — the token is in the fragment. The fragment leaks via
`Referer` on subresource requests, via browser history, and via DOM access.
A token in the fragment is a token that leaks.

The leak chain:
1. `response_type=token` → the 302 lands on `https://app/callback#access_token=ABC`.
2. The callback page loads a tracking pixel → `Referer: https://app/callback#access_token=ABC`.
3. The attacker reads the `Referer` — the token is leaked.

## Q: The app accepts `code_challenge_method=plain`. What does that buy me?

`plain` sends the `code_verifier` in the clear — equivalent to no PKCE. A
code minted with a `plain` challenge is exchangeable by anyone who saw the
authorize request.

The bypass chain:
1. `code_challenge_method=plain` → the verifier is in the URL.
2. The attacker captures the verifier from the URL or the browser history.
3. The attacker exchanges the code with the captured verifier.

## Q: The bot visits user-supplied URLs. What does that buy me?

The delivery channel for the cookie swap: a `data:text/html` URL carrying a
form that POSTs to the IdP's login endpoint, overwriting the shared jar's
SSO token. The bot's `loginSSO` step then uses your token.

The delivery chain:
1. The bot's `POST /submit-url` accepts user-supplied URLs.
2. The attacker supplies a `data:text/html` URL carrying the form.
3. The bot visits it; the form POSTs the JSON login; the `Set-Cookie`
   overwrites the SSO token.
4. The bot's `loginSSO` step uses the swapped token — the session becomes
   the attacker's account.

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
