# Evidence rules deep — the verbatim excerpts that prove each shape

The evidence-rules module names the rules. This module carries the exact
excerpts that prove each confirmed shape — what the response must contain
for the confirmation to be attributable.

## The verbatim-excerpt rule

Every confirmation requires a verbatim response excerpt — the raw bytes the
evidence was read from, not a summary. The excerpt must contain the artifact
that proves the trust break.

```bash
# capture the response verbatim
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=MISMATCHED" | tee evidence.txt

# the excerpt is the status line + the session-issuing Set-Cookie
grep -E "HTTP/|Set-Cookie:|Location:" evidence.txt
```

## Shape-by-shape evidence

### state CSRF — the confirmation

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=abc123; HttpOnly; Path=/
```

The evidence: a `302` that establishes a session — against a `state` the
session never stored. The excerpt must show the `302` and the `Set-Cookie`
that issued the session.

### state CSRF — the falsifier

```
HTTP/1.1 400 Bad Request
{"error": "state mismatch"}
```

The evidence: a `400` naming the mismatch — the `state` is bound to the
session. The excerpt must show the `400` and the error naming the mismatch.

### redirect_uri interception — the confirmation

```
HTTP/1.1 302 Found
Location: https://evil.com/callback?code=ABC&state=XYZ
```

The evidence: a `302` carrying `code=` to a URI not in the registered
allowlist — the code was delivered to the attacker. The excerpt must show
the `Location` header carrying the code to the wrong URI.

### redirect_uri interception — the falsifier

```
HTTP/1.1 400 Bad Request
{"error": "invalid redirect_uri"}
```

The evidence: a `400` naming the invalid URI — the `redirect_uri` is
validated exactly. The excerpt must show the `400` and the error naming
the rejection.

### cookie swap — the confirmation

```
HTTP/1.1 200 OK
Set-Cookie: token=NEW_TOKEN; HttpOnly; Path=/
{"status": "ok"}
```

The evidence: a `200` + `Set-Cookie` after a `text/plain` JSON login — the
SSO token was overwritten. The excerpt must show the `Set-Cookie` that
overwrote the token.

### cookie swap — the session confirmation

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=xyz789; HttpOnly; Path=/
```

The evidence: a `302` establishing a session on the attacker's account —
after the `loginSSO` step used the swapped token. The excerpt must show the
`302` and the session issued on the attacker's account.

### implicit leak — the confirmation

```
HTTP/1.1 302 Found
Location: https://app/callback#access_token=ABC&token_type=Bearer&expires_in=3600
```

The evidence: a `302` carrying `#access_token=` in the fragment — the token
is in the URL. The excerpt must show the `Location` header carrying the
fragment.

### PKCE bypass — the confirmation

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600}
```

The evidence: a `200` returning a token — for a code that was minted with a
`code_challenge` but exchanged with a wrong or missing `code_verifier`.
The excerpt must show the `200` and the token.

### cross-client — the confirmation

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600}
```

The evidence: a `200` returning a token for client B — using a code that
was minted for client A. The excerpt must show the `200` and the token,
with the `client_id=B` in the request.

### scope escalation — the confirmation

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600, "scope": "openid profile admin"}
```

The evidence: a `200` returning a token carrying a scope the app did not
request — the `admin` scope. The excerpt must show the `scope` claim
carrying the broader permission.

### registration race — the confirmation

```
HTTP/1.1 200 OK
{"status": "registered"}
```

followed by:

```
HTTP/1.1 200 OK
{"session": "abc123"}
```

The evidence: a `200` registering the account with the attacker's password,
followed by a `200` logging in as that account. The excerpt must show the
registration success and the login success.

### account linking — the confirmation

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=xyz789; HttpOnly; Path=/
```

The evidence: a `302` establishing a session on the attacker's
pre-registered account — after the OAuth login matched on `email` or
`username`. The excerpt must show the `302` and the session issued on the
attacker's account.

## The negative-result evidence

```
HTTP/1.1 302 Found
Location: /login
```

The evidence: a `302` to a login page — the flow did not complete, but no
explicit mismatch was named. The excerpt must show the `302` — a negative,
not a falsifier.

## The falsifier-vs-negative distinction in evidence

| Excerpt | What it is |
|---|---|
| `400 Bad Request: state mismatch` | falsifier — the shape is dead |
| `302 Location: /login` | negative — the flow did not complete |
| `400 Bad Request: invalid redirect_uri` | falsifier — the shape is dead |
| `302 Location: https://evil.com/callback?code=ABC` | confirmation — the shape is live |
| `200 OK` + `Set-Cookie: session=...` | confirmation — the session was issued |
| `400 Bad Request: invalid_grant` | falsifier — the code is bound |
| `200 OK` + `{"access_token": ...}` | confirmation — the token was issued |
