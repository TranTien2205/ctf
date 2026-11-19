# Troubleshoot deep — when the OAuth probes fail, with the full mechanics

The troubleshoot module names the failure shapes. This module carries the
full mechanics — why each failure happens, what the evidence actually shows,
and what to try next.

## Failure 1 — the transcript is empty

The app does not redirect to an IdP — the OAuth flow is not the login
mechanism. The evidence: `curl -i -L $BASE/login` returns a login form, not a
`302` to an IdP. Reclassify: `web-auth-session` for a local login, or a
different class for a different mechanism.

## Failure 2 — the callback 400s on everything

The app validates `state` strictly — the CSRF shape is dead. But the
`redirect_uri`, the code binding, the account linking, and the cookie jar
may still be live. The evidence: `callback?code=ABC&state=DIFFERENT` returns
`400 state mismatch`. Move to the next falsifier — `redirect_uri` validation,
`SameSite` on the SSO token, or the linking field.

## Failure 3 — the authorize URL 400s on `redirect_uri` variations

`redirect_uri` is strictly validated — the code-interception shape is dead.
The evidence: `redirect_uri=https://evil.com/callback` returns `400 invalid
redirect_uri`. Move to `state` binding, account linking, or the cookie jar.

## Failure 4 — the code exchange fails

The code is single-use, or bound to `client_id`, or bound to `redirect_uri`,
or expired. The replay is dead — but the code may still be interceptable
(via a loose `redirect_uri`) and replayable against the app's callback. The
evidence: `token` request returns `400 invalid_grant`. Move to the leak
surface — is the code in the URL? Is it in the fragment?

## Failure 5 — the text/plain JSON login 400s

The binder does not parse `text/plain` — the cookie-swap delivery is dead.
But the cookie jar may still be swappable via a different delivery: a
`application/x-www-form-urlencoded` form, a `multipart/form-data` form, or
a direct `Set-Cookie` from an XSS. The evidence: `POST /api/login` with
`Content-Type: text/plain` returns `400`. Try `application/x-www-form-urlencoded`
with a JSON-shaped body, or `multipart/form-data` with a JSON part.

## Failure 6 — the registration race loses

The bot's registerUser step ran first, or the registration is idempotent.
The race is dead — but the account may still be linkable (via the email
match), or the cookie jar may still be swappable. The evidence: `POST
/api/register` for `student@domain` returns `409 Conflict` — the account is
already registered. Move to the linking surface — does the OAuth login land
on the pre-registered account?

## Failure 7 — the `id_token` is rejected

The signature is verified, `alg=none` is not accepted, `aud`/`iss` are
validated. The `id_token` forge is dead — but the token binding may still be
loose (the `access_token` may not be bound to `client_id`). The evidence:
`id_token` with `alg=none` returns `401`. Move to the `access_token` surface —
is it bound to `client_id`? `aud`? `scope`?

## Failure 8 — the implicit flow is not accepted

`response_type` is allowlisted to `code` — the fragment leak is dead. But
the code may still leak via `Referer` on the callback page's subresources,
or via the browser history. The evidence: `response_type=token` returns `400`.
Move to the code-leak surface — is the code in the URL? Does the callback
page load a subresource?

## Failure 9 — the PKCE is required

`code_challenge` is required — the PKCE-bypass shape is dead. But the
`code_challenge_method` may accept `plain` (the verifier in the clear), or
the verifier may not be re-validated on exchange. The evidence: `authorize`
without `code_challenge` returns `400`. Try `code_challenge_method=plain` —
is the verifier sent in the clear?

## Failure 10 — the `sub` is not linkable

Linking is on `sub` — the pre-registration race is dead. But the `sub` may be
user-controlled (a self-registered username), or the `email` claim may be used
as a fallback when `sub` is absent. The evidence: the OAuth login lands on
the `sub`-mapped account — not the pre-registered one. Check whether the `sub`
is user-controlled — read the IdP's registration flow.

## Failure 11 — the flag is already submitted

The instance is consumed — the flag was submitted once at startup into an
account with an unknown random password. A fresh instance is required; the
consumed instance is a negative result, not a retriable probe. The evidence:
`GET /submission/1` returns `403` or `404` — the flag is on an unreadable
account. A fresh instance is the only fix.

## Failure 12 — the session is established but the flag is not readable

The session is the attacker's account — but the flag is on a different
account (the bot's, the teacher's, the admin's). The session is confirmed;
the sink is the next hypothesis — a `/submission/:id` gated on author email
or a teacher role. The evidence: `GET /me` returns the attacker's account —
the session is confirmed, but `GET /submission/1` returns `403` — the sink
is not reached.

## Failure 13 — the `state` is bound but the `nonce` is not

`state` is bound to the session — the CSRF shape is dead. But `nonce` may
not be validated — the `id_token` is replayable. The evidence: `callback`
with a mismatched `state` returns `400`, but a replayed `id_token` is
accepted. Move to the `nonce` surface — is it validated? bound to the
`id_token`?

## Failure 14 — the `redirect_uri` is strict but the `response_mode` is not

`redirect_uri` is strictly validated — the code-interception shape is dead.
But `response_mode=web_message` may deliver the code to a different frame —
the `postMessage` target is not validated. The evidence: `redirect_uri=https://evil.com`
returns `400`, but `response_mode=web_message` delivers the code to the
attacker's frame. Move to the `response_mode` surface.

## Failure 15 — the `client_secret` is required but leaked

The `client_secret` is required — but it is in the source, the JS bundle, the
config, or the environment. The evidence: `grep -rn "client_secret" src/`
finds it. A leaked `client_secret` makes the code exchange possible — the
stolen code is exchangeable directly.
