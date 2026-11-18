# Upgrade smuggling — a protocol upgrade sits in the path

## The shape — `Upgrade: websocket` or `Upgrade: h2c`

An upgrade request negotiates a tunnel — the front-end hands the socket to
the back-end — the smuggle lives inside the upgraded tunnel, where the
front-end no longer parses the bytes.

## The websocket upgrade — the tunnel escape

```text
GET /ws HTTP/1.1
Host: t
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x
Sec-WebSocket-Version: 13
```

Once upgraded, the front-end proxies raw websocket frames — it no longer
parses the bytes as HTTP — a smuggled HTTP request inside a frame lands
on the back-end's HTTP parser — a tunnel smuggle.

## The h2c upgrade — the cleartext-h2 tunnel

```text
GET / HTTP/1.1
Host: t
Upgrade: h2c
Connection: Upgrade, HTTP2-Settings
HTTP2-Settings: AAMAAABkAARAAAAAAAIAAAAA
```

The `h2c` upgrade speaks HTTP/2 over cleartext — the front-end proxies
h2 frames — the back-end may re-parse them as h1 — a downgrade desync —
`http2-smuggling.md`.

## The CONNECT method — the explicit tunnel

```text
CONNECT internal:80 HTTP/1.1
Host: t
```

`CONNECT` opens a raw TCP tunnel through the proxy — everything after is
raw bytes the proxy doesn't parse — a smuggle inside the CONNECT tunnel
reaches the internal host directly.

## The front-end parser-exit — when the proxy stops parsing

After an upgrade the front-end forwards bytes verbatim — no HTTP parsing,
no Host rewriting, no header injection — the back-end sees your raw bytes —
any smuggle shape works — the upgrade is the escape hatch.

## The downgrade trap — the proxy that re-parses

Some proxies upgrade the CLIENT but still parse the tunnel as HTTP —
the smuggle inside a "tunnel" is still parsed — test whether the upgrade
actually removed the front-end's parser before assuming the tunnel is raw.

## The common upgrade headers — the checklist

| Header | Signals |
|---|---|
| `Upgrade: websocket` | ws tunnel |
| `Upgrade: h2c` | cleartext-h2 |
| `Upgrade: TLS/1.2` | TLS-in-TLS |
| `Connection: Upgrade` | the upgrade flag |
| `Sec-WebSocket-*` | ws handshake |
| `HTTP2-Settings:` | h2c params |
| `CONNECT host:port` | explicit TCP tunnel |

## The upgrade-chain — upgrade → smuggle inside tunnel

```text
GET /ws HTTP/1.1                    — upgrade
Upgrade: websocket
...
                                    — upgraded; proxy proxies raw frames
GET /admin HTTP/1.1                 — inside a ws frame; back-end parses as h1
Host: t
```

The smuggled `GET /admin` inside the frame reaches the back-end's HTTP
parser — the upgrade removed the front-end's parsing — the smuggle lands.
