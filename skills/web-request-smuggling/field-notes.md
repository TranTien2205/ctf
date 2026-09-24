# Field notes — Request smuggling / CRLF injection

Written by `tools/classify_solve.py` after a flag is verified, then reviewed by a
human. Nothing here is generated from guesswork: every entry cites the solved note
and the chain card it came from.

| Status | Meaning |
|---|---|
| `proposed` | written automatically after a solve; not yet reviewed |
| `confirmed` | a human checked it against the evidence and kept it |

Promote an entry by changing its status line to `confirmed`. Delete an entry that
did not hold up, and say why in the commit message. `test/regression.py` fails if
an entry has any other status.

---

## 2026-09-11 · Weather App · proposed

- source note: `solved/weather_app.md`
- chain card: `knowledge/chains/htb-weather-app-ssrf-crlf-request-smuggling-upsert.json`
- verification: verified_live — flag returned in the login response
- classified as: `web-request-smuggling` (score 4.5, 4 signals matched)
- also matched: `web-ssrf` (4.5), `web-sqli` (3.5), `web-ssti` (2.5)
- signals that fired: Content-Length, \u010D, crlf, http://${endpoint}

**Confirming probe that worked**

> put a harmless marker with one folded space character into the interpolated field and compare the error with an ordinary hostname

Expected: the parser accepts the folded character, showing the field is not encoded

Falsifier: the field is encoded or validated, so no control characters survive

**Traps recorded on this solve**

- the injected content length must count the body bytes exactly
- a trailing request fragment is needed so the smuggled request is terminated

**Blast radius**: the upsert changes an existing account's password on a shared instance; other players lose access to that account

- status: proposed

## 2026-09-19 · Proxy · proposed

- source note: `solved/htb-proxy-smuggling-exec-stderr-oracle.md`
- chain card: `knowledge/chains/htb-proxy-smuggling-exec-stderr-oracle.json`
- verification: verified_live — The complete flag was confirmed by an anchored oracle query over the live instance: grep -q '^HTB{...}$' /flag*.txt returned HTTP/1.1 200 OK with Content-Length: 0 on the smuggled request, while the same query with one extra character appended returned HTTP/1.1 401 Unauthorized {"message":"Error flushing interface"}. Both responses were read off the live socket in the same session.
- classified as: `web-request-smuggling` (score 4.5, 4 signals matched)
- also matched: `web-ssrf` (2.5), `web-ssti` (1.5), `web-auth-session` (1.5)
- signals that fired: CRLF, Content-Length, Proxy, \r\n

**Confirming probe that worked**

> Send a single TCP write to the proxy: an allowed route with body {"a":1} and Content-Length: 7, then \r\n\r\n, then a second full request to a route the proxy's URL filter bans, with Host set to the alternate-encoded internal address. Count the HTTP status lines in the response.

Expected: Two HTTP status lines come back on the one connection, and the second belongs to the banned route (any status from the backend, including its own 4xx) rather than the proxy's 400 Bad Request. That proves the bytes after the second CRLFCRLF were forwarded unfiltered.

Falsifier: Only one status line returns, or the single response is the proxy's own 400/403 for the banned URL. Then the proxy re-serialises the request (or validates the whole buffer) and this chain does not apply — move to a different mechanism layer rather than trying more separator variants.

**Traps recorded on this solve**

- The visible first request must target a route the proxy actually forwards. Routes the proxy serves itself (/, /server-status here) never open an upstream connection, so nothing is smuggled and the probe looks like a clean falsification when it is not.
- The filler body must satisfy the backend's own body parser. express.json() answers 400 to a non-JSON filler and closes the connection before the smuggled request is read.
- Do not spend effort routing around the body blocklist once smuggling works. It only inspects bodySplit[1], so $(), backticks, ; and | are all already available in the smuggled half.
- ${IFS} expands and splits words normally - but not before an fd-numbered redirect. 'x${IFS}2>/dev/null' lexes as the word x${IFS}2 plus a bare '>', which redirects stdout and lets stderr leak; use a literal TAB there. Verified on BusyBox ash and dash.
- 'x2>/dev/null' with no separator at all is the same failure one step earlier: the word is x2 plus a stdout redirect, stderr still leaks, and a stderr-based oracle then reads false for every candidate.
- Alpine base images ship no curl. Check wget, nc, nslookup and node before concluding there is no way out.
- The flag filename may be randomised at container start (entrypoint renaming to /flag<random>.txt). Read through a glob, not a fixed path.
- Do not trust a single oracle reading. Re-send each query and include a negative control (a pattern one character off) before accepting a result.

**Blast radius**: High if the injected value is careless. The sink here runs as root inside the challenge container. The route's legitimate function flushes addresses off a network interface: passing a real interface name (eth0, lo) severs the container's networking and permanently bricks the shared instance with no way back. Always pass a name that does not exist (a bare 'x') so the legitimate command fails harmlessly, and carry the payload in the injected suffix only. Read-only conditions (grep -q, ls, test) keep the whole extraction non-destructive. Keep concurrency at one connection: the proxy reads with a fixed 1024-byte buffer and pipelining plus load makes responses unreliable. Separately, the out-of-band route sends challenge data to whatever collector is named in the URL: that is a real disclosure to a third party, so use a collector you control and never a public paste or request-bin for anything beyond a test marker. Where disclosure matters more than speed, the blind oracle keeps everything on the wire between you and the target.

- status: proposed

## 2026-09-23 · Percetron · proposed

- source note: `solved/percetron.md`
- chain card: `knowledge/chains/htb-percetron-status-mirror-haproxy-tunnel-gopher-mongo-cypher-sevenzip.json`
- verification: verified_live — HTTP 200 from GET /static/js/zz.txt whose body was the flag copied out of /flag<random>.txt on the live target
- classified as: `web-request-smuggling` (score 2.5, 2 signals matched)
- also matched: `web-parser-differential` (2.5), `web-logic-flaw` (2.0), `web-file-upload` (1.5)
- signals that fired: CRLF, haproxy

**Confirming probe that worked**

> GET /healthcheck?url=http://<your-host>:<non-default-port>/ where that host answers a bare 101, then on the same socket GET /healthcheck-dev?url=http://127.0.0.1:3000/

Expected: the first request returns 101 and the second returns an application response instead of the proxy's 403

Falsifier: the first request returns 504 (the 101 carried Upgrade/Connection and the client hung), or the second still returns 403 (the proxy did not enter tunnel mode)

**Traps recorded on this solve**

- a 101 carrying Upgrade and Connection makes a Node client raise the upgrade event, so the fetch never resolves and the proxy answers 504
- a URL whose port parseInt-s to NaN is rejected, and Node's URL normalises a default port to the empty string, so the listener needs an explicit non-default port
- the backend keep-alive timeout closes the tunnelled socket, so the second request must follow the 101 with no delay
- an application 500 closes the connection, so one tunnel carries one probe
- curl transmits NUL bytes in a gopher selector at 7.70.0 but rejects them with CURLE_URL_MALFORMAT at 8.x; measure it on the target, not on the attacking host
- gopher makes the status code 000, which becomes status 0 and throws, so a successful request is indistinguishable from a failed one by status alone
- a certificate commonName is capped at 64 characters, which constrains the injected path and forces the block-comment form

**Blast radius**: steps 6 to 8 write: one datastore document is modified, one graph node is created and a shell command runs as the application user. Pin the datastore update to your own account by username and never use a match-all filter. The shell command should write to a path you introduced, not overwrite an application file. Remove the written file and the archiver's temporary archives afterwards with a second injected certificate.

- status: proposed

## 2026-09-24 · ImageTok · proposed

- source note: `solved/htb-imagetok-bcrypt-phar-soapclient-gopher.md`
- chain card: `knowledge/chains/htb-imagetok-bcrypt-truncation-phar-soapclient-gopher-mysql.json`
- verification: verified_live — the flag came back inside the attacker's own session cookie as the single entry of the files array
- classified as: `web-request-smuggling` (score 3.5, 3 signals matched)
- also matched: `web-file-upload` (2.5), `web-ssrf` (2.5), `web-deserialization` (1.5)
- signals that fired: CRLF, Content-Length, nginx

**Confirming probe that worked**

> pad the signed blob so the identity field sits past byte (72 - secret length), rewrite it to the privileged value, keep the original signature and replay it

Expected: the server accepts the blob and re-issues a freshly signed cookie carrying the privileged identity

Falsifier: the server discards the blob and mints a new anonymous session, meaning the field is still inside the hashed prefix - add more padding

**Traps recorded on this solve**

- PHP urldecodes the POST body, so a percent-encoded payload carried in a form field must be DOUBLE-encoded (% -> %25) or it arrives as raw bytes; the chain will execute perfectly and silently insert nothing
- a deliberately pinned old dependency in the Dockerfile is the hint: curl 7.70.0 accepts %00 inside a URL while 7.74 rejects it with errno 3, and a database handshake is full of NUL bytes
- exactly three slashes after the scheme - four makes the client reject the URL as malformed
- leading whitespace also blinds parse_url but the client rejects it, so it is NOT a usable bypass; verify the client accepts whatever blinds the validator
- setcookie percent-encodes the value, so unquote before base64-decoding and re-encode before replaying, otherwise '+' is decoded back to a space and the blob is corrupted
- the destructor fires at request shutdown and the resulting fault is uncaught, so the triggering response looks like an error even when the chain worked - judge by the side effect

**Blast radius**: additive only on a shared instance: a few image uploads (a cron wipes the upload directory every two minutes) plus ONE INSERT of the flag row into the application's own files table under a chosen username. No DROP, no UPDATE of existing rows, and the datastore grant is deliberately limited. There is no delete endpoint, so that row cannot be cleaned up afterwards. The instance was also observed restarting on its own mid-run, so expect to re-fire rather than assume the payload failed.

- status: proposed
