# Handshake-side (deep) — every upgrade check, worked end to end

## The Origin enforcement matrix

| `Origin` sent | `101`-accepted | Verdict |
|---|---|---|
| the app's own origin | yes | baseline |
| `https://evil.example` | yes | the check is ABSENT → CSWSH candidate |
| `https://evil.example` | `403`/close | the check exists → probe the bypass set |
| `null` | yes | a null-origin acceptance → the bypass |
| `https://target.evil.com` | yes | a substring/`endswith` bypass |
| `https://sub.target.com` | yes | an over-permitted subdomain |
| none (non-browser) | yes | a no-Origin acceptance |
| `https://evil.example` | `403` all bypasses | the check is enforced → `uniform` |

## The auth-binding matrix

| The handshake carries | The socket binds to | The check |
|---|---|---|
| `Cookie: session=victim` | the victim session | CSWSH-able + a no-auth replay |
| `Authorization: Bearer x` | the bearer identity | a header-binding |
| `?token=<jwt>` | the token | a URL-credential → a leak |
| `Sec-WebSocket-Protocol: auth` | a protocol-selected auth | a protocol-binding |
| nothing | an unauth/default context | an unauth channel |

```bash
# the binding matrix — each carrier, then no carrier
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Cookie: session=victim' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --headers 'Authorization: Bearer x' --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws?token=eyJ" --message '{"action":"me"}'
python3 tools/web/ws_probe.py "$WS/ws" --message '{"action":"me"}'   # nothing
```

## The token-in-URL inventory

```bash
grep -riE 'wss?://[^"'\'' ]*\?|token=|jwt=|auth=|key=|api[-_]?key=|access[-_]?token=|session=' /tmp/bundle
```

- `?token=`/`?jwt=`/`?auth=`/`?key=`/`?api_key=`/`?access_token=`/`?session=`
- the URI is logged by the server/proxy and in browser history — a
  credential-in-URL finding (`web-auth-session`), independent of the
  channel's authz

## The sub-protocol matrix

```bash
for p in json graphql-ws graphql-transport-ws stomp mqtt v10.stomp v11.stomp \
         chat superchat wamp.2.json ocpp1.6; do
  echo "== $p"; python3 tools/web/ws_probe.py "$WS/ws" --headers "Sec-WebSocket-Protocol: $p" --message '{}'
done
```

- `graphql-ws`/`graphql-transport-ws` → a `web-graphql` surface
- `stomp`/`v10.stomp`/`v11.stomp`/`v12.stomp` → a STOMP command surface
- `mqtt`/`mqttv3.1` → an MQTT pub/sub surface
- a server that accepts a privileged sub-protocol → a protocol-escalation

## The upgrade-requires-auth check

```bash
# no credentials at all — does it still 101?
python3 tools/web/ws_probe.py "$WS/ws" --message '{}'
# a 101 -> the channel opens unauth (then does it drop or reply?)
# a 401/403 -> the upgrade itself is authed
```

A `101` with no credentials is a candidate — the verdict is whether the
frames then reply with data (unauth channel) or drop (closed).

## The handshake-response leak

A `101` reply carrying a `Set-Cookie`/`X-User`/`X-Role`/a session id —
the handshake response itself leaks an identity/config.

## The handshake record

`handshake: <endpoint>: <origin|binding|token|subproto|auth>: <verdict>`
— each check verbatim; a foreign-`Origin`+binding+data chain is CSWSH;
an unauth `101`+data is an unauth channel.
