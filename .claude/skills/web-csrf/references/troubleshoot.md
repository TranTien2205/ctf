# Troubleshooting — when the delivery fails

Every failure names a gate. Match the symptom to the gate that held,
then either bypass that gate or accept the falsifier.

---

## 1. The symptom→gate table

| Symptom | The gate that held |
|---|---|
| 403 + a CSRF-token error | token required & verified |
| 403 on the foreign-Origin replay | Origin/Referer enforced |
| 415 Unsupported Media Type | content-type whitelisted |
| 400 Bad Request on text/plain body | JSON parse failed — the `=` broke it |
| no state change, no error | cookie didn't attach (SameSite) OR the write is inert |
| the bot visited but nothing changed | the write didn't reach / the cookie didn't attach |
| the form submits but the endpoint 404s | wrong path / method mismatch |
| the page loads but the write doesn't fire | a JS error before the submit |
| "blocked: mixed content" | http page → https form (or reverse) |
| "blocked: private network access" | a fetch to loopback; use a form nav |

## 2. Cookie didn't attach — the SameSite read

```text
the write needs the cookie; the cookie has SameSite=Lax and the
delivery was POST/sub-resource → blocked.
- is there a GET-reachable write? → top-nav form
- is the cookie actually missing SameSite? → old-bot = attached
- is there a second cookie without the attribute? → that one ships
```

## 3. Token required — the reads

```text
- does the token live in a readable place? (a JSON endpoint, a
  meta tag, a cookie) → then the page can fetch it IF same-origin
  or CORS-open — a cross-origin page can't; a stored-on-target page can
- is the token session-bound? → replay YOUR token
- is the token double-submit? → plant the cookie + match the form
- is the token optional? → omit it
- is the token checked only on some routes/methods? → a sibling
```

## 4. Origin/Referer enforced — the bypass reads

```text
- exact-host check or substring? → substring bypassed by
  target.com.evil.com
- does absent-Origin open? → strip Referer via no-referrer, use a
  data: page (Origin: null)
- does a subdomain pass a wildcard check? → a trusted subdomain
- does the check read a proxy header? → X-Forwarded-Host spoof
```

## 5. Content-type rejected — the carrier reads

```text
- does the app parse text/plain anyway? → the sniff test
- does multipart reach a JSON-parse? → a field's value JSON-decoded
- does urlencoded reach the write? → a form-shaped body instead of JSON
- is there a different endpoint that accepts a form content-type
  and does the same write? → a sibling route
```

## 6. The write is inert — it landed but did nothing

```text
the request processed, the state didn't change:
- a field the bind ignored → check the bind model for unknown keys
- a value the validator rejected silently → check constraints
- a write to the wrong object → check the target id
- a conditional that skipped the write → check the branch
```

Read the endpoint's bind/validation — a `ShouldBindJSON` tolerates
extra keys but drops them; a strict bind rejects them.

## 7. The bot didn't fire — delivery-side failures

```text
- the URL didn't reach the bot → the submit endpoint's response?
- the page didn't load → a CSP on your host? a load error?
- the script errored before submit → put submit FIRST, or use a
  pure-HTML auto-submit shape
- the form submitted but the top-nav got cut → use an iframe-target
- the bot closed too fast → a synchronous form.submit() beats a fetch
- private-network-access blocked a fetch → a form nav isn't PNA-checked
```

## 8. The mixed-content / scheme failures

```text
an https page can't POST to http://127.0.0.1 (mixed content) →
- host the CSRF page on http (not https) if the bot allows
- or use a data: page
- or a same-scheme internal target
the TornadoService card's page POSTs to http://127.0.0.1 — the page
must be http or data:, not https, for the mixed-content rule.
```

## 9. The "the request reached but the response hid the result"

```text
a CSRF doesn't read the response — if the confirmation needs the
response (a token, the flag, an id), it's not readable cross-origin.
- does the write store the result somewhere reachable? → the readback
- does a second endpoint return it? → a follow-up read
- is the flag in the written object itself? → read the object
```

## 10. The falsifier-consolidation — when to stop

```text
after every gate is measured:
- token required AND unreadable AND session-bound → dead
- SameSite=Strict on the only credential AND no GET write → dead
- Origin/Referer enforced exactly AND required → dead via this vector
- content-type json-only AND strict AND no sibling route → dead via form
- no stored-content context AND all cross-origin gates hold → dead

when every gate holds AND no alternate vector exists → record
refutes and pivot to the class that reaches the write differently.
```

## 11. The escalation-on-spend

```bash
python3 tools/state.py <c> --strategy-used chain_match   # etc per rung
# decide.py escalate names the cheapest untried strategy — the CSRF
# that fails all gates is FALSIFIED, not "harder"; the class is done
```

## 12. The negative-result ledger

```bash
python3 tools/state.py <c> --hypothesis "gate-X-held: refutes csrf on /x"
python3 tools/hooks.py post-probe <c> --verdict refutes \
  --hypothesis-id <H> --class web-csrf \
  --evidence-kind class --evidence 'token required and session-bound' \
  --response '<the 403 body>'
```

A `refutes` with evidence is as valuable as a `confirms` — it closes
the gate and names the class boundary.
