# Falsifiers — the observations that close each shape

A falsifier is an observation that closes a specific attack shape. When it is
observed, the shape is dead — do not retry it. Record it as a falsifier, not
a negative result.

## The per-shape falsifier table

| Shape | Falsifier | What it means |
|---|---|---|
| state CSRF | `state` is cryptographically random, bound to session, single-use | the callback rejects a mismatched state — the CSRF shape is dead |
| redirect interception | `redirect_uri` is an exact match against a registered allowlist | no prefix, suffix, wildcard, or open-redirect chain delivers the code elsewhere |
| account linking | linking is on `sub` + `email_verified` enforced | an unverified email cannot link; `sub` is not attacker-controlled |
| cookie swap | SSO token cookie has `SameSite=Lax` or `Strict` | cross-site writes to the jar are rejected |
| implicit leak | `response_type` allowlisted to `code` | the token is never in the fragment |
| PKCE bypass | `code_challenge` required + `S256` + verifier re-validated | a stolen code is not exchangeable |
| cross-client | code bound to `client_id` + `aud` verified | a code or token minted for one client does not work on another |
| scope escalation | `scope` allowlisted + re-validated on exchange | the token carries only what was requested |
| registration race | registration is idempotent | a duplicate registration returns the same account, not a new one |
| code binding | code bound to `client_id` + `redirect_uri` + `state` + single-use + short expiry | a stolen code is not replayable |

## The falsifier-vs-negative distinction

| Observation | What it is | What to do |
|---|---|---|
| `400 Bad Request: state mismatch` | falsifier | the state-binding bug is dead — record the falsifier, move to the next shape |
| `302 Location: /login` | negative | the flow did not complete — record the negative, try a different probe |
| `200 OK` with the attacker's session | confirmation | the trust was broken — record the confirmation with the verbatim excerpt |
| `400 Bad Request: invalid redirect_uri` | falsifier | the redirect_uri validation is strict — the interception shape is dead |
| `302 Location: https://evil.com/callback?code=ABC` | confirmation | the code was delivered to the attacker — the interception shape is confirmed |

## The falsifier probe

```bash
# the state-binding falsifier — the cheapest first check
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=MISMATCHED"
# a 400 naming the mismatch is the falsifier
# a 302 establishing a session is the confirmation

# the redirect_uri falsifier
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://evil.com/callback&response_type=code&state=XYZ"
# a 400 naming invalid redirect_uri is the falsifier
# a 302 delivering the code to evil.com is the confirmation
```

## The falsifier ordering

Test the cheapest falsifier first:

1. `state` bound to session — one callback replay, one probe.
2. `redirect_uri` exact match — one authorize request with a wrong URI.
3. `SameSite` on the SSO token — read the `Set-Cookie` header.
4. `response_type` allowlisted — one authorize request with `token`.
5. PKCE required — one authorize request without `code_challenge`.

Each falsifier closes a shape in one probe. When all falsifiers hold, the
OAuth surface is closed — reclassify.
