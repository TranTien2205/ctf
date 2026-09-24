# Percetron — HackTheBox (web)

Flag: recorded in `challenges/percetron/state.json` via `tools/hooks.py pre-flag`
(live response, `GET /static/js/zz.txt`).
Assistance: writeup-assisted — `tools/writeup_search.py` supplied the 101/tunnel
step after the path-shape hypothesis was falsified.

## Layout

HAProxy 2.2.29 fronts an Express app on 127.0.0.1:3000. `conf/haproxy.conf`:

```
http-request deny if { path -i -m beg /healthcheck-dev }
```

`routes/generic.js`
* `/healthcheck` — `authMiddleware`, `check(url)`, then `axios.get(url, {maxRedirects: 0, validateStatus: () => true})` and **`res.status(resp.status).send()`**: the app mirrors the status of whatever it fetched.
* `/healthcheck-dev` — `authMiddleware` and **no `check()`**, straight into `getUrlStatusCode`.

`util/generic.js:getUrlStatusCode` → `execFile("curl", ["-L","-I","-s","-o","/dev/null","-w","%{http_code}", url])`.
No scheme filter, so every protocol curl was built with is reachable — and the
Dockerfile builds curl 7.70.0 from source, which includes gopher.

`entrypoint.sh` runs `mongod --bind_ip 0.0.0.0 --noauth` and renames the flag to
`/flag<10 hex>.txt`.

## The four links

### 1. Status mirroring turns HAProxy into a tunnel

`path -i -m beg` cannot be dodged by path shape: HAProxy 2.2 does not decode
percent escapes and does not normalise dot segments, while Node's `url.parse`
truncates at `#` and converts `\` to `/`. Every string Node reads as
`/healthcheck-dev` is therefore a prefix-match for HAProxy too. Measured, not
assumed — both encodings returned 404 from Express or 403 from HAProxy.

The bypass is protocol-level. Point `/healthcheck` at a server that answers
`101 Switching Protocols`; the app mirrors 101; HAProxy reads a successful
protocol upgrade, stops parsing HTTP on that connection and tunnels the raw
bytes to the backend. A second request written to the same socket reaches
Express with the ACL never evaluated.

The 101 must be **bare**. With `Upgrade: websocket` / `Connection: Upgrade`,
Node's HTTP client raises the `upgrade` event instead of `response`, axios never
resolves, and HAProxy answers 504 after `timeout server 10000`. Without them
Node reports an ordinary response whose `statusCode` is 101.

`check()` also requires `isNaN(parseInt(parsed.port)) === false`, and Node's URL
normalises a default port to the empty string, so the listener has to run on a
non-default port.

### 2. gopher → MongoDB

`/healthcheck-dev` behind the tunnel runs curl against any URL. curl 7.70.0
percent-decodes the gopher selector, transmits **NUL bytes intact** and appends
one CRLF — verified by pointing the target's gopher at a byte logger of my own
before building anything. (curl 8.x rejects `%00` with CURLE_URL_MALFORMAT, so
this is version-specific and had to be measured on the target.)

That is enough for the MongoDB wire protocol. One OP_MSG carrying

```
{update: "users", updates: [{q: {username: <me>},
                             u: {$set: {permission: "administrator"}}}],
 $db: "percetron"}
```

promotes the self-registered account; `routes/panel.js` hardcodes `"user"` at
registration and no admin is seeded, so this is the only way in.
`adminMiddleware` compares `req.session.permission`, which is filled at login,
so log in again afterwards.

The channel is blind: `%{http_code}` is `000` for gopher, `parseInt` gives 0 and
`res.status(0).send()` throws, so a successful curl always shows as HTTP 500.

### 3. Cypher injection sets `file_name`

`util/neo4j.js:addCertificate` interpolates node-forge issuer fields into a
`CREATE`:

```js
common_name: '${certInfo.issuer.commonName}',
file_name: '${certPath}',
org_name: '${certInfo.issuer.organizationName}',
```

`certPath` is server-generated, so `file_name` has to be overwritten from
`commonName`. Each field sits on its own line, so `//` cannot reach the real
`file_name` line. Open a block comment in `commonName` and close it in
`organizationName`, which swallows the real `file_name` and leaves the rest of
the map literal valid:

```
CN  = x', file_name: '<PAYLOAD>' /*
ORG = */, org_name: 'y
```

`cryptography` caps a CN at 64 characters, which caps `<PAYLOAD>` at 44.

### 4. `dl-certs` → `@steezcram/sevenzip` → shell

```js
const absolutePath = path.resolve(__dirname, filename);   // filename = file_name
const fileDirectory = path.dirname(absolutePath);
sevenzip.compress("zip", {dir: fileDirectory, destination: zipName, is64: true}, ...)
```

`@steezcram/sevenzip@1.1.6` `index.js:56`:

```js
child_process.execFile(dllPath, buildCommandArgs('compress', parameters, algorithm),
                       { shell: true, detached: false }, ...)
```

and `buildCommandArgs` pushes `` `"${parameters.dir}"` ``. With `shell: true` the
argv is joined into one shell string, so a `"` inside `dir` closes the quote.

`path.dirname` drops everything after the last `/`, so the payload carries a
throwaway final segment:

```
file_name = /a";cp /fl*.txt /app/static/js/zz.txt;"/b
dirname   = /a";cp /fl*.txt /app/static/js/zz.txt;"
shell     = 7za a -tzip "/tmp/<hex>.zip" "/a";cp /fl*.txt /app/static/js/zz.txt;"" -mm=Deflate64 -bsp1
```

`index.js` serves `/static` from `/app/static`, and the flag's random name is
covered by the `/fl*.txt` glob. `GET /static/js/zz.txt` returned the flag.

## Traps that cost time

* A 101 carrying `Upgrade`/`Connection` hangs axios — 504, not a bypass.
* `check()` rejects a URL whose port `parseInt`s to NaN, so a default-port
  listener is rejected before the fetch.
* Express's `keep-alive: timeout=5` closes the tunnelled socket; the second
  request has to follow the 101 immediately, not after a sleep.
* An Express 500 closes the connection, so one tunnel carries one probe.
* NUL over gopher works on curl 7.70.0 and not on curl 8.x — measure it on the
  target instead of on the attacking host.
* CN is limited to 64 characters, which is what forces the block-comment form
  over a longer, more readable injection.

## Cleanup

The flag copy under `/app/static/js/` and the `/tmp/*.zip` archives were to be
removed with a second injected certificate running
`rm -f /tmp/*.zip /app/sta*/js/zz.txt`. The instance was torn down before that
request landed (connection refused), so the cleanup payload never ran; the files
existed only inside the ephemeral container.
