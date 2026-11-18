# Stored CSRF, second-order, and the same-origin bypass

When every cross-origin delivery fails — Strict cookies, enforced
Origin, required tokens — the escape is delivering the CSRF page
FROM the target's own origin. A same-origin "CSRF" bypasses every
cross-origin gate.

---

## 1. The stored-delivery primitive

```text
a field that renders attacker HTML on the target's own origin:
- a stored-XSS context (the page IS on target — the form submits
  same-origin)
- a profile/bio that renders HTML
- a markdown field that doesn't sanitize tags
- an uploaded HTML page served same-origin
- a comment that renders
```

The form on the target's own page submits same-origin — no cross-
site anything. SameSite doesn't gate same-site. Origin/Referer are
the target's own. The token — the page's own JS can read the token
if it can run script; if only HTML (no JS), the form still submits
but the token field is what the page carries.

## 2. The HTML-only stored shape — no JS needed

```html
<!-- a bio field that renders HTML (not JS) -->
<form action="/transfer" method="POST">
  <input type="hidden" name="to" value="attacker">
  <input type="hidden" name="amount" value="999">
  <input type="submit" value="Click">
</form>
<!-- needs a victim CLICK — but it's same-origin, and any token the
     real form uses must be forged separately or absent -->
```

Without JS, a stored form needs a user click OR an auto-submitting
`<form>` can't fire — `<input type=image src>` clicks, an `autofocus`
+ onfocus trick needs JS. HTML-only stored CSRF needs the victim to
click — a clickjacking-adjacent shape. With a stored `<script>` or
an event-handler context, it's full XSS.

## 3. The "same-origin CSRF isn't CSRF" boundary

```text
a same-origin form that submits isn't 'cross-site' — it's just the
app's own UI misused. the class becomes relevant when:
- the stored context IS on the target but writes via the victim's
  session (stored-CSRF — a same-origin write under their cookie)
- OR the stored page's form targets a DIFFERENT internal service
  (127.0.0.1, an internal host) — a same-origin page CSRF-ing an
  internal endpoint the bot can reach
```

## 4. The second-order CSRF — the write that lands later

```text
a CSRF payload stored, then triggered by a LATER same-origin event:
- a stored profile-field CSRF that fires when an admin views the
  profile
- a stored comment that contains a form — fires when the page renders
- a stored filename/value that a later same-origin action uses
```

The second-order write rides the victim's session when they VIEW
the stored content — the CSRF is deferred.

## 5. The self-CSRF — a write the user makes against themselves

```text
a form that looks like a normal action but CSRFs the clicker:
- a 'delete my account' link that hits a GET-write
- a 'preview' button that submits a hidden write
- a profile-save form with hidden fields that over-write other data
```

The victim's own click IS the delivery — same-origin, no gate.

## 6. The internal-service second-order — the TornadoService adjacency

```text
a stored page on the target that CSRFs a 127.0.0.1/internal endpoint:
- the stored page renders on the target's origin (reachable to you)
- its form POSTs to http://127.0.0.1/internal — same 'bot is local'
  primitive as the card, but the page is stored, not your host
```

The stored page fires inside the viewer's context — when an admin
or the bot views the stored content, the form hits their loopback.

## 7. The escalation — when stored-content exists

```text
every cross-origin delivery failed (Strict/Origin/token) →
is there a stored-HTML/avatar/markdown/profile field on the target?
- yes → place the CSRF page there; it submits same-origin; the
  victim's view triggers it under their own session
- no → the class is closed for this endpoint; pivot to XSS
```

The stored-CSRF is the CSRF that survives every browser-side gate —
it's no longer cross-site, so the cross-site defenses don't apply.

## 8. The chain into class-pollution — the card's second half

```text
the TornadoService card chained CSRF → a same-origin write → class
pollution → signed-cookie forge → /stats → flag. the CSRF write
was the FOOTHOLD that enabled the next layer — a write that sets
up the next primitive.
```

The CSRF write's value often isn't the flag directly — it's the
state that unlocks the next step (a config the next layer reads, a
cookie-forge secret, a registered machine).

## 9. The falsifier

```text
no stored-content context exists AND every cross-origin delivery
fails its gate — the class is closed for this write. pivot to the
class that reaches the write differently (XSS for a stored context,
SSRF for a server-fetch, an IDOR on the write's object).
```

## 10. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "stored-csrf: profile-HTML form submits same-origin under viewer's session"
```
