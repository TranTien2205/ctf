# Real-world CSRF patterns — the recurring challenge shapes

The CSRF shapes that recur in CTF — named by what makes them work
and the trap that costs time.

---

## 1. The "the bot is localhost" family

```text
a remote_ip/localhost gate + a bot → the form-nav to 127.0.0.1
- the trap: trying header-spoofs first (X-Forwarded-For etc) — they
  fail because the gate reads the SOCKET
- the trap2: a fetch to loopback gets PNA-blocked — use a form nav
- the trap3: an https page can't POST to http loopback — use http/
  data:
```

## 2. The "shared cookie jar" family

```text
a persistent bot jar + a login endpoint → the cookie-swap
- the trap: assuming the jar is per-visit — check if it persists
- the trap2: SameSite on the token cookie blocks the cross-site set
- the trap3: the login needs a token — check the strip first
```

## 3. The "the token is decorative" family

```text
a token field present but not verified → the strip wins
- the trap: testing the token only with YOUR session's token — test
  the STRIP and a FOREIGN session
- the trap2: the check is absent-field-skips — send NO token
```

## 4. The "the GET write" family

```text
a SameSite=Lax cookie + a GET-reachable write → top-nav survives
- the trap: auditing only POST routes — the delete-link /transfer?
  is a GET
- the trap2: an <img> GET is a SUB-resource — Lax blocks it — need
  a top-nav (location=/form GET/meta)
```

## 5. The "the JSON that accepts text/plain" family

```text
a JSON endpoint that parses on body, not declared type → text/plain
- the trap: declaring Content-Type: application/json — the browser
  refuses in no-cors; ship as text/plain
- the trap2: the `=` in a form's name=value breaks the JSON — absorb
  it inside a string/dummy-key
```

## 6. The "the Origin that's decorative" family

```text
Origin/Referer present but not enforced → the foreign-Origin replay
- the trap: assuming a present Origin header = enforcement — test
  a foreign-Origin replay
- the trap2: the check is absent-allow — a data:/no-referrer page
```

## 7. The "the double-submit" family

```text
a cookie+form token → plant the cookie + match the form
- the trap: assuming the cookie can't be set — a subdomain/injection
  plants it
- the trap2: the comparison reads the wrong source — check where
  it reads cookie vs field
```

## 8. The "the stored page" family

```text
a stored-HTML/comment/profile context → the CSRF lives same-origin
- the trap: fighting the cross-site gates when a stored context
  bypasses them entirely
- the trap2: the stored page can't auto-submit without JS — needs
  a click or an autofocus trick
```

## 9. The "the credential isn't a cookie" family

```text
the ambient credential is a position/jar/IP, not a cookie →
SameSite is irrelevant
- the trap: auditing SameSite when the 'credential' is the bot's
  127.0.0.1 position — no cookie involved
- the trap2: a shared jar's persistence is the credential — the
  cookie-swap shape
```

## 10. The "the write is inert" family

```text
the CSRF lands but the write does nothing useful → a different write
- the trap: confirming 'the request fired' without checking the
  write's EFFECT — a bind that dropped the field, a validator that
  rejected the value
- the trap2: writing to the wrong object — the marker-attribution
  on YOUR object
```

## 11. The composite — the chain-card shape

```text
CSRF as the foothold: the write unlocks the next layer
- TornadoService: CSRF write → class pollution → cookie forge → flag
- SSOS: CSRF login → jar swap → bot writes flag to your account
the CSRF's value is what it enables — a write that lands but
enables nothing is the wrong write.
```

## 12. The "the write needs the bot's privilege" family

```text
a write needing admin/the bot's fixed account → deliver through
THAT viewer
- the trap: CSRF-ing a victim when the write needs the admin-bot's
  session — the privilege decides the viewer
```

## 13. The recurring trap — the "read the response" assumption

```text
expecting the flag in the CSRF's response — it's opaque. the flag
must land in a readable state (a field, a list, your account).
```

## 14. The pattern→play map

| The shape | The play |
|---|---|
| localhost gate + bot | bot-delivery form-nav to loopback |
| shared jar + login | cookie-swap via text/plain login |
| decorative token | the strip |
| GET write + Lax | top-nav GET |
| text/plain JSON | the `=`-absorption form |
| decorative Origin | foreign-Origin or absent-Origin |
| double-submit | cookie-plant + match |
| stored context | same-origin stored-CSRF |
| non-cookie credential | the position/jar primitive |
| inert write | a different write/object |
| CSRF→next-layer | the foothold write |
