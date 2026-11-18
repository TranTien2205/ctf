# The two verified chains — the grounded CSRF shapes

Two solved chains prove this class in this repository. Each is a
template — the mechanism transfers, the literals don't.

---

## 1. `htb-tornadoservice-bot-csrf-class-pollution`

### the shape
```text
a bot (admin) visits a URL you submit. an endpoint
`POST /update_tornado` accepts writes ONLY from remote_ip=127.0.0.1.
the bot's own browser resolves 127.0.0.1 to itself — a CSRF page's
form POST to 127.0.0.1 comes from the bot's socket-peer, so the
localhost gate passes for the bot, fails for you.
```

### the chain
1. direct `POST /update_tornado` from you → `403 Only localhost`
   — the gate reads `remote_ip`, the socket peer
2. header spoofing falsified — `X-Forwarded-For`, `X-Real-IP`,
   `Forwarded`, `Host` all ignored; `remote_ip` is the real socket
3. the bot is the localhost client — its browser IS 127.0.0.1
4. a cross-origin form on your page POSTs to
   `http://127.0.0.1:1337/update_tornado`
5. `enctype="text/plain"` ships raw JSON — the `=` absorbed by a
   dummy `"ignore"` key
6. Private Network Access rules make a form-navigation preferable
   to fetch — a fetch to loopback may be blocked as a private-
   network request; a form top-level nav isn't
7. the write lands → then class pollution (`__class__` reach on a
   Tornado signed-cookie secret) → forge the cookie → read `/stats`
   → the flag

### the payload
```html
<form action="http://127.0.0.1:1337/update_tornado" method="POST" enctype="text/plain">
  <input name='{"machine_id":"host-1051","ignore":"' value='"}'>
</form>
<script>document.forms[0].submit()</script>
```

### the transferable mechanism
```text
a localhost/remote_ip/private-network gate + a bot whose browser
is the local client → the CSRF page fires the write inside the
bot's context, and the gate's own check (the socket peer) is the
bot's privilege. the credential isn't a cookie — it's the bot's
network position.
```

### the falsifier that held
```text
X-Forwarded-For/X-Real-IP/Forwarded/Host spoofing all failed —
remote_ip was the real socket peer, not a header. the ONLY local
client was the bot itself.
```

## 2. `htb-ssos-oauth-registration-race-cookie-swap-json-csrf`

### the shape
```text
an SSO flow with a shared bot cookie jar. the bot holds a token
cookie that persists across visits. a registration race forces the
bot onto an attacker-controlled account; a text/plain JSON CSRF
login overwrites the shared token cookie via Set-Cookie; the bot
then submits the flag into the attacker's account.
```

### the chain
1. the bot's cookie jar persists across bot cycles — a cookie set
   in one visit survives to the next
2. a registration race — register the bot's fixed account first →
   the bot's own login fails or maps onto your account
3. the CSRF page does a text/plain JSON login to YOUR account —
   the response's `Set-Cookie: token=<yours>` lands in the SHARED jar
4. missing SameSite → the cookie-swap persists
5. the bot's loginSSO step ignores its credential arguments — it
   uses whatever token cookie the jar holds → now YOUR session
6. the bot writes the flag into YOUR account's assignment

### the payload
```html
<form action="https://sso/login" method="POST" enctype="text/plain">
  <input name='{"user":"me","pass":"x","i":"' value='"}'>
</form>
<script>document.forms[0].submit()</script>
```

### the transferable mechanism
```text
a login-CSRF into a persistent cookie jar: the CSRF doesn't write
data — it writes a CREDENTIAL. the Set-Cookie from the CSRF'd login
replaces the victim's session with the attacker's. everything the
victim does next lands on the attacker's account.
```

### the falsifier that held
```text
SameSite=Lax/Strict on the SSO cookie would block the cross-site
Set-Cookie landing — the cookie swap needs a missing SameSite or a
same-site-adjacent context.
```

## 3. The composite pattern — what both cards share

```text
both cards use a bot as the privileged actor + a form/text-plain
carrier + a credential or context the CSRF can't read but can USE:
- TornadoService: the credential is the bot's 127.0.0.1 position
- SSOS: the credential is the shared cookie jar's persistence
in neither does the attacker READ a secret — the CSRF operates on
ambient authority.
```

## 4. The decision — which card shape matches

| Observed | Card to try |
|---|---|
| a localhost/remote_ip/PNA gate + a bot | TornadoService — the bot IS the local client |
| an SSO/login + a persistent cookie jar | SSOS — login-CSRF into the shared jar |
| a bot visits attacker-controlled content | both — the delivery vehicle |
| a write gated by "local" | TornadoService |
| a write gated by a credential the CSRF can plant | SSOS |

## 5. The falsifiers each card names

```text
TornadoService falsifier: the gate reads a header you CAN spoof
  (X-Forwarded-For honored) → skip the bot, spoof directly. OR no
  bot exists → the write is unreachable.
SSOS falsifier: the cookie jar is per-visit (not shared) → the
  swap doesn't persist. OR SameSite blocks the cross-site Set-Cookie.
```

## 6. The reuse rule

```text
run tools/chain_match.py --source <dir> first — a literal signal
match returns the card to READ, not a probe to invent. a family_leads
match is a hint the mechanism exists, graded weak — it names a card
to read, never a probe to run.
```
