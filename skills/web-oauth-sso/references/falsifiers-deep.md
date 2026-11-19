# Falsifiers deep — the per-shape falsifier with the full mechanics

The falsifiers module names the observations that close each shape. This
module carries the full mechanics — why each falsifier closes the shape,
what the evidence looks like, and what to record.

## The falsifier discipline

A falsifier is an observation that closes a shape — it is not a negative
result to be retried, and it is not a confirmation to be exploited. When a
falsifier holds, the shape is dead; the next hypothesis is a different shape.

The record:

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict falsifier \
  --request "<probe>" --result "<verbatim falsifier>"
```

## Falsifier 1 — `state` bound to session + single-use

**Why it closes the shape**: `state` exists to bind the authorize request to
the callback. When it is bound to the session and single-use, a flow started
by one party cannot be completed by another — the CSRF shape is dead.

**The evidence**:

```
HTTP/1.1 400 Bad Request
{"error": "state mismatch"}
```

or:

```
HTTP/1.1 400 Bad Request
{"error": "invalid state parameter"}
```

**The probe**: `callback?code=ABC&state=DIFFERENT` — a `state` the session
never stored. A `400` naming the mismatch is the falsifier.

## Falsifier 2 — `redirect_uri` exact match + re-validated on exchange

**Why it closes the shape**: `redirect_uri` names where the code is delivered.
When it is an exact match against a registered allowlist and re-validated on
exchange, the code is delivered only to the registered URI — the interception
shape is dead.

**The evidence**:

```
HTTP/1.1 400 Bad Request
{"error": "invalid redirect_uri"}
```

or:

```
HTTP/1.1 400 Bad Request
{"error": "redirect_uri mismatch"}
```

**The probe**: `authorize?...&redirect_uri=https://evil.com/callback` — a
URI not in the allowlist. A `400` naming the rejection is the falsifier.

## Falsifier 3 — `SameSite=Lax|Strict` on the SSO token

**Why it closes the shape**: `SameSite` controls whether the cookie is sent
on cross-site requests. `Lax` allows top-level GET navigations; `Strict`
blocks all cross-site requests. Either closes the cross-site write that
overwrites the token.

**The evidence**:

```
Set-Cookie: token=ABC; HttpOnly; SameSite=Lax; Secure; Path=/
```

or:

```
Set-Cookie: token=ABC; HttpOnly; SameSite=Strict; Secure; Path=/
```

**The probe**: read the `Set-Cookie` header on the IdP's login response. A
`SameSite=Lax` or `Strict` is the falsifier.

## Falsifier 4 — `response_type` allowlisted to `code`

**Why it closes the shape**: `response_type` names the flow shape. When it
is allowlisted to `code` only, the implicit flow is not accepted — the token
is never in the fragment, and the leak surface is closed.

**The evidence**:

```
HTTP/1.1 400 Bad Request
{"error": "response_type not allowed"}
```

or:

```
HTTP/1.1 400 Bad Request
{"error": "unsupported response_type"}
```

**The probe**: `authorize?...&response_type=token` — an implicit-flow request.
A `400` naming the rejection is the falsifier.

## Falsifier 5 — PKCE required + `S256` + verifier re-validated

**Why it closes the shape**: PKCE binds the code exchange to the same client
that started the flow. When `code_challenge` is required, `code_challenge_method`
is `S256` (not `plain`), and the token endpoint re-validates `code_verifier`,
a stolen code is not exchangeable — the bypass shape is dead.

**The evidence**:

```
HTTP/1.1 400 Bad Request
{"error": "code_challenge required"}
```

or:

```
HTTP/1.1 400 Bad Request
{"error": "invalid_grant", "error_description": "code_verifier mismatch"}
```

**The probe**: `authorize?...` without `code_challenge` — a `400` naming
the requirement is the falsifier. Or `token` request with a wrong
`code_verifier` — a `400` naming the mismatch is the falsifier.

## Falsifier 6 — code bound to `client_id` + `aud` verified

**Why it closes the shape**: the code is bound to the `client_id` it was
minted for; the `aud` claim in the `id_token` names which client the token
is for. When both are enforced, a code or token minted for one client does
not work on another — the cross-client shape is dead.

**The evidence**:

```
HTTP/1.1 400 Bad Request
{"error": "invalid_client"}
```

or:

```
HTTP/1.1 400 Bad Request
{"error": "aud mismatch"}
```

**The probe**: `token` request with a code minted for client A exchanged as
client B — a `400` naming the rejection is the falsifier.

## Falsifier 7 — `scope` allowlisted + re-validated

**Why it closes the shape**: `scope` names the permissions the token carries.
When it is allowlisted per client and re-validated on exchange, the token
carries only what was requested — the escalation shape is dead.

**The evidence**:

```
HTTP/1.1 400 Bad Request
{"error": "scope not allowed"}
```

or:

```
HTTP/1.1 400 Bad Request
{"error": "invalid_scope"}
```

**The probe**: `authorize?...&scope=openid+admin` — a broader scope. A `400`
naming the rejection is the falsifier.

## Falsifier 8 — linking on `sub` + `email_verified` enforced

**Why it closes the shape**: `sub` is the IdP's stable subject identifier —
not attacker-controlled. When linking is on `sub` and `email` is only used
when `email_verified: true`, an attacker cannot register the same identity —
the linking shape is dead.

**The evidence**:

```
HTTP/1.1 400 Bad Request
{"error": "email not verified"}
```

or:

```
HTTP/1.1 302 Found
Location: /dashboard
```

(The session lands on the `sub`-mapped account, not the pre-registered one.)

**The probe**: `register` the target account with the same `email`, then
complete the OAuth flow — the session lands on the `sub`-mapped account,
not the pre-registered one. That is the falsifier.

## Falsifier 9 — registration idempotent

**Why it closes the shape**: when registration is idempotent — a duplicate
registration returns the same account, not a new one — the pre-registration
race cannot win a different password. The race shape is dead.

**The evidence**:

```
HTTP/1.1 409 Conflict
{"error": "account already exists"}
```

or:

```
HTTP/1.1 200 OK
{"status": "registered", "account_id": "existing_id"}
```

(The same account ID is returned — the registration is idempotent.)

**The probe**: `register` the same account twice — a `409` or the same
account ID is the falsifier.

## Falsifier 10 — code single-use + short expiry + bound to `state`/`nonce`

**Why it closes the shape**: a code that is single-use, short-lived, and
bound to `state`/`nonce` is not replayable — the code-interception shape
is dead.

**The evidence**:

```
HTTP/1.1 400 Bad Request
{"error": "invalid_grant", "error_description": "code already used"}
```

or:

```
HTTP/1.1 400 Bad Request
{"error": "invalid_grant", "error_description": "code expired"}
```

**The probe**: exchange the same code twice — a `400` naming the rejection
on the second is the falsifier.
