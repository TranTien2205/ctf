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

## 2026-09-26 · LockTalk · confirmed

- source note: `challenges/LockTalk/conf/haproxy.cfg`
- chain card: `knowledge/chains/htb-locktalk-haproxy-exact-path-acl-dot-segment-bypass-python-jwt-json-serialization-role-forge.json`
- verification: verified_live — Live HTB instance. GET /api/v1/./get_ticket returned HTTP 200 with a PS256 ticket carrying role=guest; that ticket on /api/v1/flag returned 403 'guest user does not have the required authorization to access the resource.'; the JSON-serialized forgery with role=administrator returned HTTP 200 and the flag in the response body. Recorded in challenges/target-31523/state.json through tools/hooks.py post-probe (confirms, evidence-kind class then impact) and pre-flag (source live-response). Solve shape: 8 requests of recon and 2 probe sweeps; no writeup was consulted for either half. Mechanism corrected after the handout arrived: the ACL is path_beg,url_dec -i (conf/haproxy.cfg:16), and the exact-match behaviour was then reproduced offline against haproxy:2.8.1-alpine in a two-config differential (with vs without the converter).
- classified as: `web-parser-differential` (score 0.0, 0 signals matched)
- also matched: `web-auth-session` (1.5), `web-ssrf` (1.0), `web-logic-flaw` (0.93)
- filed by operator override: the matcher did not rank this class; the chain is filed under the class whose first probe opens it

**Confirming probe that worked**

> GET /api/v1/./get_ticket with curl --path-as-is, next to a plain GET /api/v1/get_ticket

Expected: the plain path returns the proxy's HTML 403 'Request forbidden by administrative rules.' and the dot-segment path returns HTTP 200 with {"ticket: ":"eyJhbGciOiJQUzI1NiI..."} — one request apart, proving the ACL is matched literally and the backend normalises

Falsifier: both return 403 (the ACL is a prefix match, or the proxy normalises before matching — try //, ;, %2e, a trailing slash and case next), or both return 404 (the route never existed and the 403 was about something else)

**Traps recorded on this solve**

- THE RULE IS WEAKER THAN IT READS, and this was measured, not assumed. conf/haproxy.cfg:16 says  http-request deny if { path_beg,url_dec -i /api/v1/get_ticket }  which reads as a prefix deny. Reproduced offline against haproxy:2.8.1-alpine with the same backend: WITH the ',url_dec' converter, /api/v1/get_ticket/ and /api/v1/get_ticket/x are ALLOWED (200); with the converter removed they are DENIED (403). Appending a converter to the path_beg shorthand drops its implicit -m beg and the rule degrades to an exact string match. The author added url_dec to harden against percent-encoding and silently turned a prefix deny into an exact-path deny.
- the dot-segment bypass does NOT depend on that bug: /api/v1/./get_ticket returned 200 in BOTH configs in the offline differential, because HAProxy does not resolve dot segments while Werkzeug does. That is the portable half of this finding -- it works against a correctly written path_beg too.
- url_dec did not even help where it was meant to: /api/v1/%2e/get_ticket is allowed in both configs, because the decoded form /api/v1/./get_ticket does not begin with the blocked prefix either. It then 404s at Flask because Werkzeug does not percent-decode before route matching.
- use curl --path-as-is. Without it curl collapses /api/v1/./get_ticket to /api/v1/get_ticket client-side and the bypass silently does not happen -- the probe then reports a false negative on a working payload.
- /api/v1//get_ticket answers 308, not 200 -- Werkzeug merges the duplicate slash and redirects. It is real evidence that normalisation exists, but it is not itself the bypass; //api/v1/get_ticket (leading, not interior) returns 200 directly.
- the query string is not part of the path sample: /api/v1/get_ticket?x=1 is still denied. Do not waste a probe on it.
- the forged token is a JSON object, not a compact JWT, and it is sent as the whole Authorization header value. It contains spaces, braces and quotes; send it verbatim without URL-encoding and without a Bearer prefix (middleware.py:9 reads the raw header).
- the two leading spaces in the crafted key are load-bearing: they keep the JSON key distinct and are discarded by base64 decoding along with { and ", so split('.')[0] still decodes to the genuine header. Dropping them breaks the header parse.
- do not recompute or re-sign anything. The protected, payload and signature members must be byte-identical to the issued ticket or jwcrypto rejects the token before python_jwt ever reads the forged claims. The signing key is generated per boot (config.py), so there is nothing to recover.

**Blast radius**: Read-only end to end. Every step is a GET; nothing is written to the target and there is nothing to clean up. The forged token is accepted for the lifetime of the ticket it was built from (one hour here), so re-fetch a ticket rather than reusing a stale forgery.

- status: confirmed

## 2026-09-26 · SerialFlow · confirmed

- source note: `challenges/SerialFlow/challenge/application/app.py`
- chain card: `knowledge/chains/htb-serialflow-werkzeug-octal-cookie-memcached-injection-pylibmc-flag1-pickle-rce.json`
- verification: verified_live — Live HTB instance. The chain was first validated end to end against a local container built from the supplied Dockerfile (GET /static/f.txt returned the placeholder the container's placeholder flag), then run once against the target: inject 200, resync after 3 polls, trigger 200, and GET /static/f.txt returned the real flag. Recorded in challenges/target-30968/state.json through tools/hooks.py post-probe (confirms, evidence-kind class then impact) and pre-flag (source live-response). Cleaned up with a second RCE round.
- classified as: `web-parser-differential` (score 0.0, 0 signals matched)
- also matched: `web-auth-session` (0.98)
- filed by operator override: the matcher did not rank this class; the chain is filed under the class whose first probe opens it

**Confirming probe that worked**

> GET / with Cookie: session="AA\101BB", next to a plain Cookie: session=AAABB

Expected: both answer 200 and both echo Set-Cookie: session=AAABB — the octal escape was decoded server-side, so arbitrary bytes can be pushed into the session-store key

Falsifier: the echo comes back as the literal AA\101BB or quoted (no octal decoding, so there is no byte channel), or the request 500s (the value is validated before it reaches the store)

**Traps recorded on this solve**

- USE PICKLE PROTOCOL 0 -- this is the requirement that actually matters. The cookie reaches Flask as a str, so protocol 2 (which starts with \x80) is re-encoded as multi-byte UTF-8, the set's byte count no longer matches the data, and the value is silently never stored. Flask-Session itself serialises with dumps(..., 0) for the same reason.
- flags 0 and flags 1 BOTH give execution, and an early measurement here said otherwise. With protocol 0 and a resynced connection both were re-measured and both ran the command: flags 1 unpickles inside pylibmc's client.get(), flags 0 is unpickled by Flask-Session's own serializer.loads. The first 'flags 0 does nothing' reading came from a protocol-2 payload on a desynced connection -- two confounders at once. Do not conclude a negative from a single run against a flapping instance.
- use pickle protocol 0. Protocol 2 starts with \x80, and the cookie reaches Flask as a str, so every byte >= 0x80 is re-encoded as multi-byte UTF-8 and the set's byte count no longer matches the data -- the value is silently not stored. Flask-Session itself serialises with dumps(..., 0) for the same reason.
- the injection request ALWAYS returns 500 and that is not failure. open_session's get carries the injection and succeeds; save_session then reuses the same poisoned sid in a set, which memcached rejects ('bad command line format' / 'bad data chunk') and pylibmc raises. Verify the injection by reading the key out of memcached, never by the HTTP status.
- that same 500 leaves the app's single shared pylibmc connection desynced, so the trigger usually fails if sent immediately. Poll with RANDOM cookies until one returns 200 before triggering -- random cookies cannot clobber the payload key, whereas re-requesting the payload key lets save_session overwrite it with a normal flags-0 session.
- a failed trigger is safe to retry: its save_session also fails, so the overwrite does not happen and the payload survives. A SUCCESSFUL trigger does overwrite it, so re-inject before each new attempt.
- raw control bytes in the Cookie header do not work and a percent-encoded %0d%0a is not decoded either. Only the quoted-string octal form is decoded (verified: "AA\101BB" -> AAABB, while "AA\x41BB" -> AAx41BB).
- do not read anything into the length-boundary flapping: this instance intermittently returned 500 for lengths that later returned 200. Re-measure a suspicious boundary twice with two distinct keys before building a theory on it -- one such false reading sent this solve chasing a non-existent client-side key check.
- the container cannot be restarted with docker restart: entrypoint.sh chmods itself to 600 on first run, so a restart fails with 'permission denied'. Use docker rm -f plus docker run for a fresh instance, and poll the app over HTTP for readiness -- docker's port proxy accepts connections before Flask is listening, so a bare TCP connect is not a readiness check.

**Blast radius**: The injection corrupts the app's single shared memcached connection every time, so the app 500s and sometimes resets connections until it recovers; on a shared instance that is a visible outage of a few seconds. The RCE runs as root. Keep the command additive and reversible: this solve created /app/application/static/f.txt, read it over HTTP and then removed the directory with a second round (verified 404 afterwards, with / still 200). Do NOT overwrite application/templates/index.html, which is what public writeups do -- that destroys the only page the app serves and cannot be undone without a rebuild.

- status: confirmed

## 2026-09-27 · Wizard Shop · confirmed

- source note: `challenges/wizardshop/state.json`
- chain card: `knowledge/chains/htb-wizardshop-haproxy-exact-path-acl-double-slash-login-sqli-unlimited-2fa-brute.json`
- verification: verified_live — Live HTB instance. /auth/login -> 403 'Request forbidden by administrative rules.' while //auth/login -> 200 with <form action="/auth/login" method="POST">; username="admin' --" -> 302 location /auth/verify-2fa; the boolean oracle read users = 1:admin:<32-char plaintext password>; /auth/verify-2fa gave 20x400 then 10x429 while //auth/verify-2fa gave 30x400; code 0438 answered 302 to /dashboard with session=eyJhdXRoZW50aWNhdGVkIjp0cnVlfQ..., and //dashboard with that cookie returned 'Welcome, here is your flag: HTB{...}'. Recorded in challenges/wizardshop/state.json through tools/hooks.py post-probe (confirms, evidence-kind class three times then impact) and pre-flag (source live-response).
- classified as: `web-parser-differential` (score 1.25, 1 signals matched)
- also matched: `web-request-smuggling` (1.0)
- signals that fired: //auth/login, /./auth/login, /auth/./login and /auth%2f

**Confirming probe that worked**

> GET /auth/login and GET //auth/login with curl --path-as-is, and compare the bodies rather than only the status codes

Expected: the first returns a 403 whose body is the proxy's own page ('Request forbidden by administrative rules.'), the second returns the application's login form

Falsifier: both return the same error page, or the 403 body is in the application's own error format -- then the denial is the app's and no path trick can move it

**Traps recorded on this solve**

- curl collapses /./ and // client-side unless --path-as-is is passed, so the bypass silently fails to fire and reads as a dead end. Pass it on every probe in this family.
- /auth//login is NOT a bypass here: Werkzeug merges the duplicate slash and answers 308, so a redirect-following client reports the 403 it was redirected into. Only the LEADING double slash works.
- /AUTH/LOGIN answers the Flask 404, so case variation is not a bypass -- Werkzeug routes are case-sensitive. Do not spend probes on it.
- the boolean oracle needs the comment form. username="admin' AND '1'='1" answers 400 because the password clause survives, which looks like the injection failing; it is the injection working with a wrong payload shape. Use "admin' AND (<predicate>)--".
- python's urllib RAISES the 302 as an HTTPError when a redirect handler declines the redirect, so the TRUE case of the oracle arrives in the except branch and a naive `r.status == 302` check reports every row as FALSE. This cost a full extraction run before it was caught.
- the pending login has no cookie and lapses. Once it does, every 2FA attempt answers 302 -> /auth/login, which is 'not 400' and so reads as a hit to any brute-forcer whose success test is negative. Test for the ACTUAL success shape (302 to /dashboard, or a Set-Cookie) and re-login when the /auth/login redirect appears.
- immediately after the correct code is accepted, concurrent in-flight attempts answer 500 rather than 400, because the state they were racing has been consumed. Three codes adjacent to the real one answered 500 in this solve; none of them was valid.
- one isolated 403 in the middle of a brute-force run is the proxy, not a hit. Re-test any candidate serially before believing it.

**Blast radius**: The brute force is the dangerous part on a shared instance. The pending login is SERVER-SIDE with no cookie, so every attempt runs against state shared by everyone on that instance: a successful guess consumes it for whoever else was mid-login, and the traffic is thousands of requests in a burst. Keep the pool small, batch it, and stop at the first hit -- this solve stopped after 438 codes. The SQL injection is read-only as used here (a SELECT in the login), but the same injection point reaches an UPDATE-free statement only by luck, so do not extend it with stacked queries. Nothing was written to the target and nothing needs cleaning up.

- status: confirmed
