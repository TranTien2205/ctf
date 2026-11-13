# Authentication & session attacks

**When:** login, registration, password reset, remember-me, JWT/cookie
sessions, OAuth flows. The highest-value surface on most real apps.

## Session token analysis - first move

Feed any JWT/opaque token to `jwt_decode`:

- `alg=none` -> `jwt_forge` emits a signature-free variant to resend
- HS256 + weak secret recovered offline -> `jwt_forge` re-signs with claim
  overrides (`sub`, `role`, `admin`) - you cannot compute HMAC yourself.
  A recovered secret is itself a finding; the forged request returning a
  200 echoing your claims is the verbatim proof.
- RS256 -> alg confusion: re-sign with the public key as HS256 secret
- `kid`/`jku` header -> traversal to a known file, or attacker-controlled
  JWKS URL when in scope
- Claims worth flipping: `role`, `admin`, `scope`, `tenant`, `exp`, `nbf`

Opaque cookies: check length/charset for hash-of-data, base64(JSON) blobs,
Django/Flask signed cookies (`itsdangerous`, `eyJ...:sig`), Rails
`_session` (encrypted+signed - needs key), ASP.NET `__VIEWSTATE`-adjacent
formats.

## Login surface

- User enumeration: different error for bad user vs bad pass; timing;
  registration "already exists"; reset "if the account exists" vs 404
- `probe_lockout` sends a bounded burst (<=15) of bad-credential attempts:
  429/lockout text/growing latency = throttled; identical failures =
  unthrottled guessing (a standard report line - do NOT brute force
  beyond proof on a real target)
- Default/common creds on a lab or staging only: admin/admin, demo/demo
- SQLi on login fields (see `sqli` auth set)
- Response manipulation: server returns `{"success":false}` - try
  flipping client-side handling only if JS gates it

## Password reset - walk it end to end

- Token in reset URL: predictable? short? reused? never expires?
- `Host` header poisoning -> reset link with attacker domain (in scope)
- Token not bound to account: your token + victim email field
- Multi-use tokens: request twice, use the first

## Session management checks

- Session id NOT rotated at login -> session fixation
- `HttpOnly`/`Secure`/`SameSite` flags absent (fingerprint reports these)
- Logout does not invalidate server-side (old cookie still works)
- Long-lived remember-me with weak entropy

## Registration / mass assignment

`probe_massassign` POSTs the JSON template plus privilege fields the form
never sends (`role`, `is_admin`, `admin`, `verified`). An injected field
appearing in the response means the server binds untrusted input - and that
is only a candidate, because a write echoing its own input proves it was
accepted, not that it was stored.

Pass `read_url` (the base the created object is served from; the id in the
write's response is appended) and the probe does the read-back for you.
Quote the privileged field **and its value** as that read returns it - e.g.
`"role": "admin"` - not the response at large: the gate matches the pair the
write sent and requires that value absent from the read's own request.

## Severity guide

Forged session/token: critical. Full account takeover path: critical-high.
User enumeration only: low-medium. Missing cookie flags: low-medium.
Unbounded login attempts with weak-password policy: medium.
