# Troubleshoot — when the OAuth probes fail

The OAuth audit fails in predictable ways. This module names the failure
shapes and what to try next.

## The transcript is empty

The app does not redirect to an IdP — the OAuth flow is not the login
mechanism. Reclassify: `web-auth-session` for a local login, or a different
class for a different mechanism.

## The callback 400s on everything

The app validates `state` strictly — the CSRF shape is dead. But the
`redirect_uri`, the code binding, the account linking, and the cookie jar
may still be live. Move to the next falsifier.

## The authorize URL 400s on `redirect_uri` variations

`redirect_uri` is strictly validated — the code-interception shape is dead.
Move to `state` binding, account linking, or the cookie jar.

## The code exchange fails

The code is single-use, or bound to `client_id`, or bound to `redirect_uri`,
or expired. The replay is dead — but the code may still be interceptable
(via a loose `redirect_uri`) and replayable against the app's callback.

## The text/plain JSON login 400s

The binder does not parse `text/plain` — the cookie-swap delivery is dead.
But the cookie jar may still be swappable via a different delivery: a
`application/x-www-form-urlencoded` form, a `multipart/form-data` form, or
a direct `Set-Cookie` from an XSS.

## The registration race loses

The bot's registerUser step ran first, or the registration is idempotent.
The race is dead — but the account may still be linkable (via the email
match), or the cookie jar may still be swappable.

## The `id_token` is rejected

The signature is verified, `alg=none` is not accepted, `aud`/`iss` are
validated. The `id_token` forge is dead — but the token binding may still
be loose (the `access_token` may not be bound to `client_id`).

## The implicit flow is not accepted

`response_type` is allowlisted to `code` — the fragment leak is dead. But
the code may still leak via `Referer` on the callback page's subresources,
or via the browser history.

## The PKCE is required

`code_challenge` is required — the PKCE-bypass shape is dead. But the
`code_challenge_method` may accept `plain` (the verifier in the clear), or
the verifier may not be re-validated on exchange.

## The `sub` is not linkable

Linking is on `sub` — the pre-registration race is dead. But the `sub` may
be user-controlled (a self-registered username), or the `email` claim may
be used as a fallback when `sub` is absent.

## The flag is already submitted

The instance is consumed — the flag was submitted once at startup into an
account with an unknown random password. A fresh instance is required; the
consumed instance is a negative result, not a retriable probe.

## The session is established but the flag is not readable

The session is the attacker's account — but the flag is on a different
account (the bot's, the teacher's, the admin's). The session is confirmed;
the sink is the next hypothesis — a `/submission/:id` gated on author email
or a teacher role.
