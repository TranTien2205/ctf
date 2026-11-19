# Workflow — the OAuth audit sequence

The OAuth audit is a bounded sequence: walk the flow once, name the trust
that is broken at each step, test the cheapest falsifier first, and close each
shape before moving to the next.

## Phase 1 — the transcript

Walk the whole flow once with a clean jar. Record every redirect, parameter,
cookie set, and who set it. The transcript is the exploit surface.

```bash
# capture the full flow
curl -i -b "$JAR" -c "$JAR" -L "$BASE/login" 2>&1 | tee transcript.txt
grep -E "Location:|Set-Cookie:|HTTP/|code=|state=|client_id=|redirect_uri=|scope=|nonce=" transcript.txt
```

Record: the `authorize` URL's parameters, the `callback` URL's parameters,
every `Set-Cookie` with its attributes, and the session-establishing response.

## Phase 2 — the falsifier sweep

Test the cheapest falsifiers first, in order:

```bash
# 1. state binding — one callback replay
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=MISMATCHED"
# 400 naming mismatch = falsifier; 302 establishing session = confirmation

# 2. redirect_uri validation — one authorize request
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://evil.com/callback&response_type=code&state=XYZ"
# 400 naming invalid = falsifier; 302 delivering code = confirmation

# 3. SameSite on the SSO token — read the Set-Cookie
grep -i "Set-Cookie.*token" transcript.txt
# SameSite=Lax|Strict = falsifier; missing or None = live

# 4. response_type allowlist — one authorize request
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=token&state=XYZ&nonce=N"
# 302 to fragment = live; 400 = falsifier

# 5. PKCE required — one authorize request without code_challenge
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
# accepted = live; 400 = falsifier
```

## Phase 3 — the confirmation

When a falsifier does not hold, the shape is live. Confirm it:

```bash
# state not bound — replay the callback, record the verbatim response
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=MISMATCHED" | tee evidence.txt

# the evidence is the response that issued the session
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict confirms \
  --evidence-kind class \
  --evidence "$(grep -E 'HTTP/|Set-Cookie:' evidence.txt | head -3)" \
  --response "$(cat evidence.txt)"
```

## Phase 4 — the escalation

When a shape is confirmed, the next step is the exploitation shape that turns
it into impact:

| Confirmed shape | The escalation |
|---|---|
| state not bound | the login-CSRF or linking-CSRF — the victim's session lands on the attacker's account, or the attacker's identity links to the victim's account |
| redirect_uri loose | the code-interception — the code is delivered to the attacker's endpoint |
| account linking on email | the pre-registration — the attacker registers the target account first |
| cookie swap | the text/plain JSON login — the SSO token is overwritten cross-site |
| implicit leak | the fragment-harvest — the token leaks via Referer or history |
| PKCE bypass | the stolen-code exchange — the code is exchangeable without a verifier |
| cross-client | the code replay — a code minted for one client works on another |
| scope escalation | the broader token — the token carries more permissions than requested |
| registration race | the pre-registration — the attacker owns the account the bot registers |

## Phase 5 — the negative ledger

Every probe that produces no new signal is a negative result. Record it:

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict negative \
  --request "replay callback with mismatched state" \
  --result "400 Bad Request: state mismatch"
```

The negative ledger is the kill map — it tells the next agent which shapes
are already closed.

## The budget

Five probes or fifteen active minutes per mechanism class. Twenty-five probes
or forty-five active minutes for the whole challenge. When the budget is
exhausted, `tools/decide.py` answers `escalate` — the next rung is a
different mechanism, a reclassify, or a writeup search.
