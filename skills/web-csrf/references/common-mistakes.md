# Common mistakes — the ways CSRF analysis goes wrong

Each entry is a real failure mode: what it looks like, why it fails,
and the fix.

---

## 1. "The endpoint returned 200" ≠ "the CSRF worked"

```text
the delivery's HTTP status says the REQUEST reached the server —
not that the write happened, not that the cookie attached, not that
a token wasn't required. the proof is the STATE CHANGE read back.
```

Fix: read the object, not the delivery's status.

## 2. Testing the token-check with YOUR OWN token

```text
grabbing YOUR session's CSRF token and replaying it in the CSRF
page — if the token is session-bound, this proves nothing about the
victim's session. if it's NOT session-bound, your token validates
the victim's write — which IS the bug, but you must verify it
validates under a DIFFERENT session, not assume.
```

Fix: replay your token under a different session/cookie — does it
still validate?

## 3. Assuming SameSite=Lax blocks everything

```text
SameSite=Lax blocks cross-site POST/fetch/img — but NOT top-level
GET navigations. a GET-write under Lax is still reachable. the
missed case: a state change reachable by GET.
```

Fix: check whether ANY write is GET-reachable before declaring Lax
a falsifier.

## 4. Forgetting the `=` problem in text/plain JSON

```html
<!-- WRONG — the form's name=value join puts = between keys -->
<input name='{"a":1' value='"b":2}'>
<!-- body: {"a":1="b":2} — invalid JSON -->
```

Fix: every form-`=` must land INSIDE a JSON string — use a dummy
key or a real free-text field to absorb it.

## 5. A stored page that can't run JS still needs a click

```text
a stored-HTML context (bio, comment) that renders HTML but not JS:
a <form> needs a user CLICK to submit — no auto-submit without JS.
the CSRF becomes a clickjacking-adjacent shape — needs the victim
to click the submit. plan for the interaction or get JS execution.
```

Fix: a stored context without JS = a click-required CSRF — the form
needs `type=submit` + a social hook, or an `<input type=image>`.

## 6. Content-type confusion — declaring vs sending

```js
// setting Content-Type: application/json in a fetch — the browser
// REFUSES it in no-cors mode (needs a preflight no-cors won't do)
fetch(url,{mode:'no-cors',headers:{'Content-Type':'application/json'}})
// silently becomes text/plain or fails — the JSON never ships as json
```

Fix: in no-cors, only `text/plain`/`urlencoded`/`multipart` content-
types are settable — ship the JSON body AS text/plain and hope the
server parses on body not declared type.

## 7. Mixed-content — https page → http form

```text
a page on https://attacker posting to http://127.0.0.1 → the browser
blocks it as mixed content. the TornadoService card's page POSTs to
http loopback — it must be on http or a data: URL, not https.
```

Fix: host the CSRF page on http, or use data:text/html, or match
the scheme.

## 8. Private Network Access — fetch to loopback blocked

```text
a fetch('http://127.0.0.1/x') from a public page → Chrome's PNA
blocks it as a private-network request from a public context.
a FORM NAVIGATION to the same host isn't PNA-checked the same way —
the card used a form, not fetch.
```

Fix: use a form top-level navigation for loopback targets, not
fetch/xhr.

## 9. The "read the response" assumption

```text
a CSRF is fire-and-forget — the response goes to the frame/nav and
is unreadable cross-origin. expecting 'the flag in the response' is
wrong — the response is invisible. the flag must land somewhere
YOU read back separately.
```

Fix: design the write to place the result in a readable state — a
field, a record, your own account.

## 10. Re-testing the same delivery

```text
submitting the identical page again after a failure — if a gate
held once, it holds again. each retry costs a bot cycle.
```

Fix: name the gate that held, change the delivery to bypass THAT
gate, or accept the falsifier.

## 11. Ignoring the GET-write surface

```text
auditing only POST endpoints — a GET-with-side-effect (a delete-link,
a transfer-GET) is CSRF-able even under Lax via a top-nav.
```

Fix: grep for GET routes that mutate — `/delete?id=`, `/transfer?`,
`/admin?action=`.

## 12. The "no token = vulnerable" shortcut

```text
no CSRF token field ≠ vulnerable — Origin/Referer enforcement,
SameSite=Strict, or a content-type gate may still close it. the
token is ONE gate of five.
```

Fix: measure ALL gates — cookie attribute, Origin/Referer, content-
type, the write's reachability — not just the token.

## 13. A foreign-Origin 200 misread as "no enforcement"

```text
a foreign-Origin request returning 200 might mean the endpoint
ignores Origin — OR the endpoint processed but the write needs a
cookie that didn't attach. the 200 alone doesn't prove the write.
```

Fix: the foreign-Origin replay is a HEADER-enforcement test; the
cookie-attach is a separate question (SameSite). Both must pass.

## 14. The credential-swap without readback

```text
a login-CSRF that swaps the victim to your account — if you never
read YOUR account for the victim's deposit, you proved nothing.
```

Fix: the login-CSRF's readback is YOUR account's state — read it.

## 15. Over-crediting a family_leads match

```text
a chain_match family_leads entry is mechanism-vocabulary — graded
weak, a card to READ, never a probe to run. treating it as a proven
match invents a probe.
```

Fix: read the named card, then run ITS first_confirming_probe —
don't treat the family match as the finding.
