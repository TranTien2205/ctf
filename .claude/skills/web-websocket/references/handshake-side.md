# Handshake-side — the upgrade checks, complete

## The Origin check — the CSWSH surface

```bash
# the foreign-Origin probe
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://evil.example' --message '{}'
# -> 101 = accepted -> CSWSH-candidate
# -> 403/close = the check exists -> the bypass set
```

```bash
# the bypass set — the full nine
python3 tools/web/ws_probe.py "$WS/ws" --origin 'null' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'file://' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://target.evil.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://eviltarget.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://target.com.evil.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://sub.target.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://target.com.attacker.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://targetcom.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'   # no Origin
```

A `101` on ANY of these = the check is absent or bypassed.

## The auth-binding check

```bash
# the cookie-binding
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=victim' --message '{"action":"me"}'
# -> {"user":"victim",...} = the cookie bound the socket
# the bearer-binding
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Authorization: Bearer <t>' --message '{"action":"me"}'
# the URL-token binding
python3 tools/web/ws_probe.py "$WS/ws?token=<jwt>" --message '{"action":"me"}'
# the custom-header binding
python3 tools/web/ws_probe.py "$WS/ws" --headers 'X-Api-Key: <k>' --message '{"action":"me"}'
```

The binding names the credential the socket trusts — the cookie for
CSWSH, the `?token=`/`Bearer` for the token-attacks.

## The unauth check

```bash
# no credential at all
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'
# -> 101 + a data reply = an unauth channel
# -> 101 + drop-all = a closed channel (a gap)
# -> 401/403/close = the upgrade is authed
```

## The token-in-URL check

```bash
# the credential on the URI
grep -riE 'wss?://[^"'\'' ]*\?' /tmp/bundle
# -> ?token=/?jwt=/?key=/?auth=/?session=/?api_key=
```

A credential in the URI -> logs/history/referer — a `web-auth-session`/
`web-info-disclosure` finding, independent of the channel's authz.

## The sub-protocol check

```bash
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: graphql-ws' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: stomp' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Sec-WebSocket-Protocol: mqtt' --message '{}'
```

An accepted alternate sub-protocol -> a `web-parser-differential`/
weaker-authed protocol.

## The SameSite read — the CSWSH leg

```bash
curl -sI "$BASE/login" | grep -i 'set-cookie'
# -> Set-Cookie: session=x; SameSite=Lax|None|Strict
```

`Strict` -> the browser blocks the cookie cross-site — CSWSH's browser
leg fails; `Lax`/`None` -> the cookie travels.

## The first-frame auth check

```bash
# the auth moved into a frame
python3 tools/web/ws_probe.py "$WS/ws" --message '{"type":"auth","token":"<x>"}'
python3 tools/web/ws_probe.py "$WS/ws" --message '40{"token":"<x>"}'
python3 tools/web/ws_probe.py "$WS/ws" --message '{"type":"connection_init","payload":{"authToken":"<x>"}}'
```

An auth-frame -> a forgeable/stale/null token check — `web-auth-session`.

## The handshake-record

`handshake: <endpoint>: <origin|binding|unauth|token|subproto|samesite>:
<the verdict>` — each check verbatim; the verdict is the measured reply.
