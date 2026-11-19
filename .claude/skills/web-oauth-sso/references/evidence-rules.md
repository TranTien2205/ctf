# Evidence rules — what counts as a confirmation

The OAuth flow is a sequence of redirects and cookie writes. The evidence for
a confirmation must tie the observed session to the specific trust that was
broken — not just that a session was established.

## The verbatim rule

Every confirmation requires a verbatim response excerpt — the raw bytes the
evidence was read from. The excerpt must contain the artifact that proves
the trust break: the `Location` header carrying the code to the wrong URI,
the `Set-Cookie` overwriting the SSO token, the session ID issued against a
mismatched state.

```bash
# the evidence is the response that carried the artifact
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=MISMATCHED" | tee evidence.txt
# the excerpt must quote the status line and the session-issuing Set-Cookie
```

## The confirmation shapes

| Claim | The evidence that confirms it |
|---|---|
| state not bound | a `callback` response that issues a session against a state the session never stored |
| redirect_uri loose | a `302 Location:` carrying `code=` to a URI not in the registered allowlist |
| code not bound to client | a `token` response returning a token for a code minted for a different `client_id` |
| account linking on email | an OAuth login that lands on the attacker's pre-registered account |
| cookie swap | a `loginSSO` response that issues a session on the attacker's account after the SSO token was overwritten |
| implicit leak | a `302 Location:` carrying `#access_token=` in the fragment |
| PKCE not enforced | a `token` response returning a token without a `code_verifier` |
| scope escalation | a `token` response carrying a scope the app did not request |

## The negative-result rule

A probe that produces no new signal is a negative result — record it as such,
with the probe and the boundary it tested. A `400` naming the mismatch is a
falsifier — it closes the path. A `302` to a login page is a negative — the
flow did not complete.

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict negative \
  --request "replay callback with mismatched state" \
  --result "400 Bad Request: state mismatch"
```

## The falsifier rule

A falsifier is an observation that closes the class — it is not a negative
result to be retried. When the falsifier is observed, the class is closed;
the next hypothesis is a different class.

| Falsifier | What it closes |
|---|---|
| `state` bound to session + single-use | the CSRF shape |
| `redirect_uri` exact match + re-validated on exchange | the code-interception shape |
| `sub`-based linking + `email_verified` enforced | the account-linking shape |
| `SameSite=Lax|Strict` on the SSO token | the cookie-swap shape |
| `response_type` allowlisted to `code` | the implicit-leak shape |
| PKCE required + `S256` + verifier re-validated | the PKCE-bypass shape |
| code bound to `client_id` + `aud` verified | the cross-client shape |
| scope allowlisted + re-validated | the scope-escalation shape |

## The ordering rule

The evidence must tie the session to the specific step whose trust was broken.
A session established after a mismatched-state callback is evidence for the
state-binding bug — not for the redirect_uri bug. Record which step's trust
was broken; the next hypothesis is a different step.
