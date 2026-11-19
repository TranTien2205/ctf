# CSWSH — cross-site WebSocket hijacking, the whole attack

## The mechanism — a realtime CSRF

`new WebSocket("wss://target/ws")` from a page on YOUR origin — the
browser treats the upgrade as a GET and attaches the victim's cookies.
The socket opens AS the victim. You read and write the victim's live
channel — messages, presence, privileged actions.

## The precondition chain — all four

1. the handshake accepts a foreign `Origin` (no allowlist check)
2. the handshake binds the socket to the session COOKIE (auth by cookie,
   not a token the attacker page cannot read)
3. the victim's cookie is `SameSite=None`/`Lax` or a top-level context
   (so it travels on the cross-site upgrade)
4. the channel carries victim data or accepts a privileged action

## The probe — `ws_probe.py` foreign-Origin

```bash
# the direct check — a foreign Origin + a session cookie
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --headers 'Cookie: session=victim' --message '{"action":"me"}'
# a 101 + a reply -> the foreign Origin is accepted and the session binds
```

- `101` accepted → the Origin check is absent
- `403`/close → the check exists; try the bypass set
- a reply carrying victim data → the binding + the data read

## The Origin-bypass set — a partial check

```bash
for o in 'null' 'https://target.evil.com' 'https://eviltarget.com' \
         'https://target.com.evil.com' 'https://target.com' \
         'null' 'file://' 'https://sub.target.com'; do
  echo "== Origin: $o"; python3 tools/web/ws_probe.py "$WS/ws" --origin "$o" --message '{}'
done
```

A substring/`endswith`/regex-miss check — `*.target.com`, `target.com*`,
a `null`/`file:` origin — bypasses it.

## The SameSite caveat — does the cookie travel?

- `SameSite=Strict` — the cookie does NOT travel on a cross-site upgrade
  → CSWSH fails (modern browsers)
- `SameSite=Lax` (default) — travels on a TOP-LEVEL navigation; a
  `new WebSocket` from a sub-frame/script may or may not — test it
- `SameSite=None` — travels → CSWSH
- a `partitioned`/CHIPS cookie — the third-party cookie is partitioned

The SameSite rule decides whether the victim's cookie reaches your
socket — read `Set-Cookie: ... SameSite=` first.

## The token-in-URL alternative

If the socket auths by a `?token=` the attacker page CANNOT read, a
foreign `Origin` does not help — the page lacks the token. CSWSH needs
the cookie-binding; a URL-token kills it (unless the token leaks).

## The impact — what the hijacked socket buys

- READ — the victim's live channel: messages, notifications, presence,
  a flag field in a subscription reply
- WRITE — a privileged action `{"action":"admin"}`/a `send` as the
  victim → a state change
- a `web-xss`-free exfil — your page `fetch`es the exfil to your server

## The CSWSH vs CSRF boundary

- `web-websocket` — the CSWSH (the socket channel)
- `web-csrf` — a one-shot forged request (no read-back)
- the CSWSH is strictly stronger — it reads the replies AND maintains
  the channel
- a `web-auth-session`/`web-oauth-sso` if the auth-binding is a token
  the attacker CAN obtain

## The CSWSH record

`cswsh: <accepted-origin> + <session-binding> + <data-read>` — the
four preconditions, the verbatim accepted-`Origin` reply, and the
victim-data read or the privileged action it produced.
