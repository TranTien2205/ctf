# Desync shapes — every ambiguous byte sequence

## The CL.TE shape — `CL:4 TE:chunked`

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked
<body>
```

## The TE.CL shape — same bytes, different read

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked
<body>
```

Same bytes — the disagreement is in the parser — `desync-taxonomy.md`.

## The TE.TE shape — the obfuscated TE

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: cow
<body>
```

`obfuscation.md`.

## The CL.CL shape — the dup-CL

```text
POST / HTTP/1.1
Content-Length: 4
Content-Length: 7
<body>
```

`cl-manipulation.md`.

## The CL.0 shape — the ignored-body

```text
POST /ignored HTTP/1.1
Content-Length: 60
<the smuggle>
```

`client-side-desync.md`.

## The H2.CL shape — `content-length:0` inside h2

```text
:method POST :path / content-length 0 + DATA bytes
```

`http2-smuggling.md`.

## The H2.TE shape — `transfer-encoding:chunked` inside h2

```text
:method POST :path / transfer-encoding chunked
```

`http2-smuggling.md`.

## The fold shape — `%0d%0a` inside a value

```text
?host=x%0d%0aX-Inj:%201
```

`crlf-injection.md`.

## The upgrade shape — `Upgrade: ws` + smuggle

```text
GET /ws Upgrade:websocket + HTTP inside frame
```

`upgrade-smuggling.md`.

## The CONNECT shape — `CONNECT host:port` + raw

```text
CONNECT internal:80 + raw HTTP
```

`tunneling.md`.

## The dup-Host shape — `Host: a` + `Host: b`

```text
GET / HTTP/1.1
Host: a
Host: b
```

`virtual-host.md`.

## The absolute-URI shape — `GET http://internal/path`

```text
GET http://internal/path HTTP/1.1
```

`header-smuggling.md`.
