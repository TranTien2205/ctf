# Field manual — the OAuth audit at a glance

The OAuth audit is a bounded sequence. This manual is the checklist you run
in order — each step names the probe, the expected signal, and what to do next.

## Step 0 — walk the flow

```bash
curl -i -b "$JAR" -c "$JAR" -L "$BASE/login" 2>&1 | tee transcript.txt
```

Record every redirect, parameter, cookie set, and who set it. The transcript
is the exploit surface — the cookie swap, the state mismatch, the redirect
chain all live in the ordering of writes.

## Step 1 — the cookie inventory

```bash
grep -i "Set-Cookie" transcript.txt
```

For each cookie, record: `SameSite`, `HttpOnly`, `Secure`, `Domain`, `Path`.
Two cookies — one from the app, one from the IdP — in the same jar is the
swap signal.

## Step 2 — the parameter inventory

```bash
grep -oP 'authorize\?[^"]+' transcript.txt | tr '&' '\n'
```

Record `client_id`, `redirect_uri`, `response_type`, `state`, `scope`, `nonce`,
`code_challenge`, `code_challenge_method`. Each is a testable surface.

## Step 3 — the falsifier sweep (cheapest first)

| # | Probe | Confirmation | Falsifier |
|---|---|---|---|
| 1 | callback with mismatched state | session issued | `400 state mismatch` |
| 2 | authorize with wrong redirect_uri | code delivered | `400 invalid redirect_uri` |
| 3 | authorize with `response_type=token` | fragment leak | `400` or code-only allowlist |
| 4 | authorize without `code_challenge` | accepted | `400` or PKCE required |
| 5 | SameSite on the SSO token | missing or `None` | `Lax` or `Strict` |

## Step 4 — the shape confirmation

When a falsifier does not hold, the shape is live. Confirm it with the verbatim
response that carries the artifact:

- `Location: https://evil.com/callback?code=ABC` — the code was delivered to
  the attacker.
- `Set-Cookie: token=NEW; HttpOnly` after a text/plain JSON login — the SSO
  token was overwritten.
- `HTTP/1.1 200` with the attacker's session — the trust was broken.

## Step 5 — the escalation

| Confirmed shape | The escalation |
|---|---|
| state not bound | the login-CSRF or linking-CSRF |
| redirect_uri loose | the code-interception |
| account linking on email | the pre-registration race |
| cookie swap | the text/plain JSON login |
| implicit leak | the fragment-harvest |
| PKCE bypass | the stolen-code exchange |
| cross-client | the code replay |
| scope escalation | the broader token |
| registration race | the pre-registration |

## Step 6 — the negative ledger

Every probe that produces no new signal is a negative result. Record it:

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict negative \
  --request "<probe>" --result "<verbatim result>"
```

## The decision tree

```
Is there a second cookie (IdP token) in the jar?
  YES → check SameSite → missing/None → cookie-swap shape live
  NO  → single-cookie model → move to state/redirect_uri

Is state bound to session?
  NO  → state CSRF live → login-CSRF or linking-CSRF
  YES → falsifier → move to redirect_uri

Is redirect_uri strictly validated?
  NO  → code-interception live
  YES → falsifier → move to account linking

Is linking on email/username?
  YES → pre-registration race live
  NO  → falsifier → move to implicit/PKCE/cross-client
```
