# Negative results deep — the OAuth observations that are not confirmations

The negative-results module names the discipline. This module carries the
full mechanics — why each observation is a negative, what it actually
proves, and what to do next.

## The negative discipline

A negative is an observation that does not confirm the shape — the request
went through, the response came back, but the artifact that proves the trust
break is not there. A negative is not a falsifier (the shape is not dead)
and it is not a confirmation (the shape is not live). It is a measurement
that did not reach the sink.

## Negative 1 — the callback accepts a mismatched `state` but issues no session

```
HTTP/1.1 302 Found
Location: /login
```

The `302` is to a login page — the flow did not complete, but no explicit
mismatch was named. The `state` may be bound to the session (the `302` is
the app's own login redirect), or the code may be invalid (the `302` is the
error path). The evidence is ambiguous — a negative, not a falsifier.

What to do: re-run with a valid `state` and an invalid `code` — the `302` is
the error path; re-run with an invalid `state` and a valid `code` — the `302`
is the `state` rejection. The discrimination is in the `Location`.

## Negative 2 — the authorize accepts a wrong `redirect_uri` but issues no code

```
HTTP/1.1 302 Found
Location: https://app/callback?error=invalid_request
```

The `302` carries `error=invalid_request` — the IdP rejected the request,
but the rejection is on a different parameter (missing `client_id`,
`response_type`, or `scope`), not on `redirect_uri`. The `redirect_uri` may
be validated, or the request may be malformed. A negative, not a falsifier.

What to do: re-run with a valid request and a wrong `redirect_uri` — if the
`400` names `redirect_uri`, it is the falsifier; if the `302` carries a
code, it is the confirmation.

## Negative 3 — the `text/plain` JSON login returns `200` but no `Set-Cookie`

```
HTTP/1.1 200 OK
{"status": "ok"}
```

The `200` is the login's own response — but no `Set-Cookie` follows. The
login may have succeeded but the cookie is set by a different mechanism
(a JS `document.cookie` write, a `refresh` token, a different endpoint).
The `Set-Cookie` is the artifact — its absence is a negative.

What to do: check the response headers for `Set-Cookie` on a different
attribute (`Path`, `Domain`, `Max-Age`); check the body's `Set-Cookie`
header (a JS-rendered page may carry it).

## Negative 4 — the `id_token` is accepted but the `aud` is not verified

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600}
```

The `200` returns a token — but the `aud` in the `id_token` is not verified.
The cross-client shape is live, but the token is bound to the `client_id`
it was minted for — not to the attacker's `client_id`. The confirmation is
in the token's `aud` claim, not in the `200`.

What to do: decode the `id_token` — read the `aud` claim. If it is the
attacker's `client_id`, the cross-client shape is confirmed; if it is the
victim's `client_id`, the shape is live but the token is not usable.

## Negative 5 — the registration race wins but the OAuth login does not link

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=xyz789; HttpOnly; Path=/
```

The `302` establishes a session — but on the `sub`-mapped account, not the
pre-registered one. The registration race won, but the linking is on `sub`,
not `email`. The session is confirmed; the sink is not reached.

What to do: check the linking field — `sub`, `email`, `preferred_username`.
If the linking is on `sub`, the pre-registration race is dead; if the `sub`
is user-controlled, the race is still live.

## Negative 6 — the `code` is replayable but the `state` is bound

```
HTTP/1.1 400 Bad Request
{"error": "state mismatch"}
```

The `code` is replayable — the exchange did not fail — but the `state` is
bound to the session. The code-interception shape is live (the code can be
stolen), but the session cannot be issued (the `state` is not the victim's).
The shape is live but the chain is broken.

What to do: check whether `state` is bound to the session or to the `code`.
If `state` is bound to the `code`, the stolen code is replayable; if `state`
is bound to the session, the stolen code is not replayable.

## Negative 7 — the `SameSite` is missing but the `loginSSO` reads credentials

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=xyz789; HttpOnly; Path=/
```

The `SameSite` is missing — the cross-site write lands — but the `loginSSO`
step reads credentials, not the jar's token. The session is issued on the
attacker's own account, not the swapped one. The cookie-swap shape is dead
for this app.

What to do: check the `loginSSO` step — does it read the jar's token, or
does it read the request's credentials? If it reads credentials, the swap
is dead; if it reads the jar's token, the swap is live.

## Negative 8 — the `code_challenge` is required but `code_challenge_method` accepts `plain`

```
HTTP/1.1 400 Bad Request
{"error": "code_challenge required"}
```

The `code_challenge` is required — the PKCE shape is not dead — but
`code_challenge_method=plain` may still be accepted. The required-challenge
falsifier holds for the no-challenge shape, but the plain-method shape is
still live.

What to do: `code_challenge_method=plain` — is the verifier sent in the
clear? If yes, the PKCE shape is live via the plain-method bypass.

## Negative 9 — the `scope` is broader but the app does not use it

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600, "scope": "openid profile admin"}
```

The `scope` is broader — the token carries `admin` — but the app's endpoints
do not check the `scope` claim. The scope-escalation shape is live (the
token is broader), but the sink is not reached (the app does not enforce
scope).

What to do: check what the broader scope unlocks — a `read:write` scope on
an endpoint that checks `scope`, an `offline_access` scope that issues a
refresh token, or an `admin` scope on an endpoint that checks `admin`.

## Negative 10 — the `response_type=token` is accepted but the fragment is not leaked

```
HTTP/1.1 302 Found
Location: https://app/callback#access_token=ABC&token_type=Bearer&expires_in=3600
```

The `response_type=token` is accepted — the token is in the fragment — but
the callback page does not load a subresource that leaks the `Referer`. The
implicit-leak shape is live (the token is in the fragment), but the leak
surface is not reached.

What to do: check the callback page's subresources — a tracking pixel, a
script, an image. If the page loads a subresource, the `Referer` carries
the fragment; if not, the leak is not reachable.
