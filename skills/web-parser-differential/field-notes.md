# Field notes — Parser differential / proxy trust

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

## 2026-09-07 · NovaCore · proposed

- source note: `solved/novacore.md`
- chain card: `knowledge/chains/htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce.json`
- verification: verified_live — flag file read by the executed plugin
- classified as: `web-parser-differential` (score 3.5, 3 signals matched)
- also matched: `web-file-upload` (3.5), `web-prototype-pollution` (3.5), `web-xss` (3.5)
- signals that fired: hop-by-hop, traefik, x-real-ip

**Confirming probe that worked**

> send the same authenticated-only request twice, once normally and once with the proxy header named in the Connection header

Expected: the second request is accepted without a token

Falsifier: both requests are rejected, so the trust check does not depend on that header

**Traps recorded on this solve**

- the bot runs on a fixed schedule; place the poisoned state first, then poll
- the polyglot only works when the archive bytes are overlaid at the offset the scanner reads

**Blast radius**: overwriting a neighbouring cache entry corrupts another user's record; plugin execution runs code on the instance

- status: proposed

## 2026-09-19 · Dusty Alleys · proposed

- source note: `solved/htb-dusty-alleys-default-vhost-leak-ssrf-key-header.md`
- chain card: `knowledge/chains/htb-dusty-alleys-http10-host-vhost-leak-ssrf-to-header-mirror.json`
- verification: verified_live — the flag was returned inline by the live target as the value of the key field in the JSON the mirroring endpoint produced for the server-side fetch
- classified as: `web-parser-differential` (score 2.5, 2 signals matched)
- also matched: `web-ssrf` (4.5), `web-request-smuggling` (2.5), `web-sqli` (1.5)
- signals that fired: nginx, x-forwarded-for

**Confirming probe that worked**

> request the reflecting endpoint using the older protocol version with an empty host header, and compare the reflected host with the one returned by an ordinary request

Expected: the reflected host is an internal domain name rather than the address that was dialled

Falsifier: the reflected host is unchanged, or the proxy rejects the request outright

**Traps recorded on this solve**

- the loopback target must be addressed by the name the application expects: an address literal made the fetcher fail with an invalid status code error, while the name on the same port succeeded
- the proxy normalises dot-dot segments before choosing a location, so traversal from the proxied prefix falls back to the static root instead of reaching another backend path
- combining a content length with a chunked encoding is rejected by the proxy, so smuggling is not the way into the unproxied backend routes
- the reflecting endpoint looks like a harmless debug route; its real value is that it prints credentials attached by a server-side fetcher

**Blast radius**: read-only. Every step is a GET, and the server-side fetch should be pointed only at the challenge's own loopback services. Do not aim the url parameter at anything outside the supplied instance, and do not use it as a general relay.

- status: proposed

## 2026-09-23 · NovaCore · proposed

- source note: `solved/novacore.md`
- chain card: `knowledge/chains/htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce.json`
- verification: verified_live — flag file read by the executed plugin. Re-verified live 2026-09-23 on a second instance: GET /api/trades returned 401 plain and 200 with 'Connection: close, X-Real-Ip', and the recorded solver then produced the flag from run_plugin output with only the HOST/PORT line changed.
- classified as: `web-parser-differential` (score 4.5, 4 signals matched)
- also matched: `web-file-upload` (3.5), `web-prototype-pollution` (3.5), `web-xss` (3.5)
- signals that fired: headers.get("X-Real-IP, hop-by-hop, traefik, x-real-ip

**Confirming probe that worked**

> Send the same token-gated API request twice, once plain and once with the proxy-added header listed in the Connection header. Pick the endpoint out of the source first: a 404 on both arms means the path is wrong, not the technique.

Expected: The plain request is rejected (401) and the hop-by-hop one is accepted (200).

Falsifier: Both arms return the same status. If that status is 401 the trust check does not depend on that header; if it is 404 the endpoint name is wrong and the probe has not tested anything.

**Traps recorded on this solve**

- the bot runs on a fixed schedule; place the poisoned state first, then poll
- the polyglot only works when the archive bytes are overlaid at the offset the scanner reads
- The app reads X-Real-IP while the proxy writes X-Real-Ip. Header lookup is case-insensitive so it does not matter, but it makes a hand-written probe easy to mis-copy.
- A 404 on BOTH arms of the differential probe means the endpoint is wrong, not that the proxy bypass failed. Read the blueprint for the real route names before concluding anything.
- The Server header shows the app server, not the proxy, so 'no proxy in front' cannot be inferred from it. The 401-vs-200 split is what proves a proxy is adding the header.
- The overflow corrupts a neighbouring cache record and the plugin step executes code: both are inherent to the chain, so run it only on an instance you own.

**Blast radius**: overwriting a neighbouring cache entry corrupts another user's record; plugin execution runs code on the instance

- status: proposed

## 2026-09-23 · stored XSS behind S/MIME (secure-email-service) · proposed

- source note: `solved/secure-email-service.md`
- chain card: `knowledge/chains/pico-secure-email-service-header-colon-differential-utf7-mt19937.json`
- verification: verified_live — the flag was read from the GET /api/emails response body on the live target, delivered there by the admin bot's own browser POSTing localStorage.flag to /api/send
- classified as: `web-parser-differential` (score 0.0, 0 signals matched)
- also matched: `web-ssti` (3.5), `web-xss` (3.5), `web-race-condition` (2.5)
- filed by operator override: the matcher did not rank this class; the chain is filed under the class whose first probe opens it

**Confirming probe that worked**

> send one message whose Subject is 'x\nFrom : <other identity>', then read back what the application's own parser reports as the sender

Expected: the parser reports the injected identity, not the genuine From header the generator wrote

Falsifier: the generator rejects the newline, or the parser still reports the genuine sender, meaning the space-before-colon form is not honoured

**Traps recorded on this solve**

- the injected boundary delimiter is itself part of the message text, so email.generator._make_boundary() matches '^--<b>(--)?$', calls it a collision and re-rolls the boundary to '<b>.0' -- the prediction is right and the exploit still fails silently; a single trailing space on the delimiter line defeats the anchored regex and is still a legal RFC 2046 delimiter
- the same attacker string is used for BOTH the Subject header and the template body, so every injected line must also survive the generator's header guard; keep a space before any colon and no colon before the first whitespace on a line
- CPython normalises a lone CR to LF inside a header value, so a bare \r is not a way around the guard
- verify the generator's version from the Dockerfile: a newer local CPython adds verify_generated_headers and rejects payloads the target accepts
- the recovered PRNG state dies with the process, so collection, recovery and attack must run in one pass
- a boundary that collided reads as '<digits>==.0' and will not match a strict '={15}\d{19}==' regex, which makes a signed message look unsigned in your own tooling

**Blast radius**: read-only against the target's own data, but the bot endpoint is globally serialised behind a lock and each run costs ~15s; the collection phase writes several hundred messages into your own mailbox, so never point it at a shared account.

- status: proposed

## 2026-09-24 · in-office · confirmed

- source note: `solved/cscv-inoffice.md`
- chain card: `knowledge/chains/cscv-inoffice-authority-form-acl-bypass-restricted-pickle.json`
- verification: verified_live — flag string read from the body of GET / on the live instance after the leak pickle Supporting observation: POST office-process?,mmoffice.x.corp returned 200 OK with body 'It works!'
- classified as: `web-parser-differential` (score 1.5, 1 signals matched)
- also matched: `web-file-upload` (3.5), `web-ssrf` (3.5), `web-request-smuggling` (2.5)
- signals that fired: haproxy

**Confirming probe that worked**

> GET office-process?,mmoffice.x.corp HTTP/1.1 with Host: office-process?,mmoffice.x.corp

Expected: 405 METHOD NOT ALLOWED from Flask, proving both that HAProxy's path ACL did not fire and that Werkzeug routed the bare token to the POST-only /office-process

Falsifier: 403 Forbidden (path ACL still matched), 503 (hdr(host) no longer matched so no backend), 400 Bad request (HAProxy rejected the authority/Host pair), or 404 (the target did not route to the protected view)

**Traps recorded on this solve**

- HAProxy rejects authority-form with 400 unless the authority is byte-equal to Host, so the route token and the required vhost must be smuggled into the same string and separated by a comma for hdr() to split them
- a port in the authority breaks the backend side: urlsplit('office-process:80') parses office-process as a scheme and leaves path '80'
- no URI whose path sample is set can hide the substring: in every form HAProxy accepts, its authority scan and Python's netloc end at the same '/', and url_dec decodes exactly like Python's unquote, so a failing url_dec leaves a literal % that Werkzeug cannot route
- the SSRF at /healthcheck is a dead end for delivery: urlopen with only method/url/headers can never emit a body, because http.client's _is_illegal_header_value permits only obs-fold, which never terminates the header block, and POST without data always sends Content-Length: 0
- gunicorn honours a SCRIPT_NAME request header only from a peer in forwarded_allow_ips (127.0.0.1,::1); through the proxy it is dropped by header_map=drop, so the SCRIPT_NAME prefix-strip trick works when testing the backend directly and silently fails through HAProxy
- /healthcheck returns 'error' for any 4xx/5xx because urlopen raises HTTPError, so a 2xx status code is the only positive oracle it gives

**Blast radius**: step 4 mutates live in-process Flask state on a shared instance: replacing view_functions['index'] changes / for every other player until restored, so always send the step 5 restore pickle immediately after reading the flag. The unpickle sink is arbitrary builtins-level code in the container; open(..., 'w') on /app is harmless because the source tree is mounted read-only, but the same primitive can kill the worker.

- status: confirmed
