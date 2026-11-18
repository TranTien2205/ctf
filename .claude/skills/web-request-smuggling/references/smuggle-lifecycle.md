# Smuggle lifecycle — the end-to-end path

## Step 1 — the injection — the ambiguous request

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

The ambiguous request — both a valid CL-request and a valid TE-request
— `desync-taxonomy.md`.

## Step 2 — the front's parse — the front reads CL

The front-end reads `Content-Length: 4` → body = `5c\r\n` → forwards
the request (plus the extra bytes) to the back-end's socket.

## Step 3 — the back's parse — the back reads TE

The back-end reads `Transfer-Encoding: chunked` → `5c` = 92 bytes of
chunk data (which includes the smuggled `GET /admin`) → then `0` →
the smuggle's bytes become the NEXT request.

## Step 4 — the smuggle executes — `GET /admin` runs

The back-end runs `GET /admin` — as the back-end itself — the front's
filter never saw it — `frontend-bypass.md`.

## Step 5 — the response goes to the wrong socket

The back-end answers `GET /admin` — the response goes to the NEXT
request on the queue — `response-poisoning.md`.

## Step 6 — the readback — the smuggle's output reaches you

The next request's response IS the smuggle's — the self-poison or the
stored readback — `smuggle-readback.md`.

## Step 7 — the flag — the verbatim excerpt

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<the verbatim excerpt>"
```

## The failure points — where it dies

- the front rejects the ambiguous request → `400` — `denies`
- the front honors TE too → no disagreement — `denies`
- the back rejects the smuggle → `400`/`500` — the framing is wrong
- the connection isn't shared → no next request — `denies`
- the smuggle's `Host:`/`CL` is wrong → `404`/hang
- the readback doesn't reach you → blind-smuggle — `blind-smuggle.md`
