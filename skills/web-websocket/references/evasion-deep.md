# Evasion (deep) — the check taxonomy and the bypass grammar

## The Origin-check bypass grammar

```bash
# the 9-shape Origin bypass set — run the whole set
python3 tools/web/ws_probe.py "$WS/ws" --origin 'null'                      --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'file://'                    --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://target.evil.com'    --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://eviltarget.com'     --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://target.com.evil.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://sub.target.com'     --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://target.com.attacker.com' --message '{}'
python3 tools/web/ws_probe.py "$WS/ws" --origin 'https://targetcom.com'      --message '{}'
# and NO Origin at all — a non-browser client
python3 tools/web/ws_probe.py "$WS/ws"                                       --message '{}'
```

The bypass classes: `null`/`file:` (the null-origin), `*.target.com`
(subdomain), `target.evil`/`eviltarget`/`target.evil.com` (substring/
endswith), `targetcom`/`target-attacker` (a similar-name), no-`Origin`
(a non-browser).

## The auth-binding bypass grammar

- a `?token=` that is forgeable/predictable — `web-auth-session`'s JWT/
  token attacks
- a `connection_init`/`40{"token"}`/`{"type":"auth"}` frame that
  OVERRIDES the handshake with a controlled token
- a `Sec-WebSocket-Protocol` selecting a weaker-auth protocol
- a stale/again-valid `?token=`/`?session=` — a non-rotated credential
- a `X-Forwarded-For`/`X-Real-IP` the IP-check reads — a spoofed header

## The per-message filter bypass grammar

```json
{"action":"x","role":"admin"}              -> a self-grant
{"action":"x","user":{"role":"admin"}}      -> a nested-merge grant
{"action":"x","perm":["admin"],"scope":"*"} -> an array/type-juggle
{"action":"x","__proto__":{"role":"admin"}} -> pollution
{"action":"x","Role":"admin"}              -> a case-variant field
{"action":"x","role":"ADMIN"}              -> a case-variant value
{"action":"x","is_admin":true,"debug":1}    -> a truthy/int juggle
{"action":"x","role":" admin "}            -> whitespace-trim bypass
```

## The injection-field bypass — the payload's evasion

- the WS transport bypasses an HTTP-layer WAF — the frame carries the
  raw payload the `POST`-body filter never sees
- a unicode/`%`/double-encoded payload — `web-sqli`'s/`web-ssti`'s
  encoding evasion
- a split-payload across fragments (`fin=0`) — a per-fragment filter
  sees only part
- a compressed `permessage-deflate` frame — a content-filter inspecting
  uncompressed bytes misses it

## The replay/resume bypass

- a `reconnect` that resumes the LAST authed context without re-auth
- a `resume`/`session_id` field replaying an old session
- a `seq`/`offset`/`lastEventId` field requesting old frames (the feed
  history) — a history-IDOR

## The rate/throttle bypass

- a per-CONNECTION limiter → N sockets, one probe each
- a per-frame-rate limiter → a slower cadence
- a per-message-type limiter → a different action name
- a reconnect that resets a per-connection counter

## The parser-differential evasion

A frame that parses differently at the proxy/filter vs the app —
`web-parser-differential`-shaped: a duplicate `action`/`id` key, a
`__proto__` pollution, an over-long field, a `+`/unicode mutation — the
filter's schema does not match the app's.

## The evasion-discipline

A bypass is a finding — a broken control — not a license for an
unbounded sweep. Record `evasion: <check>: <bypass>`; the bypass itself
is the vulnerability evidence.
