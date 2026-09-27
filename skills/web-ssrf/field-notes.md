# Field notes — Server-side request forgery

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

## 2026-09-07 · Red Island · proposed

- source note: `solved/red-island.md`
- chain card: `knowledge/chains/htb-red-island-ssrf-gopher-redis-lua-rce.json`
- verification: verified_live — flag returned by the helper binary through the Lua channel
- classified as: `web-ssrf` (score 2.5, 2 signals matched)
- also matched: `web-request-smuggling` (2.5), `web-race-condition` (1.5), `web-auth-session` (1.5)
- signals that fired: 127.0.0.1, ssrf

**Confirming probe that worked**

> submit a loopback URL in the fetch field and read the full response body, including error text

Expected: content or an error that proves the server performed the fetch

Falsifier: the field is validated to an allowlist and never reaches a client

**Traps recorded on this solve**

- the gopher payload length prefix must equal the exact byte length of the Lua string
- always read error bodies: this app leaked the fetched file inside a non-200 message

**Blast radius**: eval on the shared Redis instance affects every player's session; prefer read-only Lua first

- status: proposed

## 2026-09-23 · ArtificialUniversity · proposed

- source note: `solved/htb-artificial-university-grpc-attribute-pollution-eval.md`
- chain card: `knowledge/chains/htb-artificial-university-grpc-attribute-pollution-eval.json`
- verification: verified_live — After the two bot visits, GET /static/f.txt returned the flag in the response body; a follow-up run with an idempotent cleanup expression removed the file and the same path then returned 404, with the application still answering 200 on /.
- classified as: `web-ssrf` (score 3.5, 3 signals matched)
- also matched: `web-cors` (3.0), `web-prototype-pollution` (2.5), `file-read-primitives` (2.5)
- signals that fired: 127.0.0.1, pdf, url=

**Confirming probe that worked**

> Create an order whose price is 0 through the branch that takes the price from the request, then call the success endpoint with a payment_id that starts with a slash and navigates the privileged browser to an ordinary, observable endpoint (for example one that creates a record you own).

Expected: The record appears under your own account, proving the bot ran, that the price gate is satisfiable, and that the leading slash escapes the fixed prefix.

Falsifier: No record appears. Either the amount check is real, or the parameter is sanitised, or the prefix cannot be escaped — in which case the privileged browser cannot be steered and the rest of the chain does not apply.

**Traps recorded on this solve**

- An embedded font program's own /FontMatrix overrides the one in the font dictionary, defusing the font-matrix injection with no visible error. Blank it in place and keep the byte length so the stream lengths stay valid.
- Relative URLs inside a PDF viewer context resolve against the viewer's internal base rather than the document URL, so a same-origin-looking fetch fails. Use absolute URLs.
- A prefix glued in front of the parameter makes 'prefix..' a literal segment; the payload has to start with a slash before '../' works.
- Tunnel providers that hand out a random subdomain per reconnect will silently invalidate a payload that has the hostname baked in. Rebuild the delivered file per request from the current hostname and keep the tunnel under a restart loop, or two runs will look like exploit failures when the host was simply dead.
- A flag filename randomised at container start has to be globbed, not named.
- int() over a subprocess's stdout plus a global error handler that returns the exception args leaks that stdout in the response body — a free read channel worth checking for.
- The polluted attribute cannot be removed through the merge. Overwrite it with something that returns a valid value instead of leaving a destructive expression behind.

**Blast radius**: Moderate and mostly reversible if handled deliberately. The injected expression runs as root inside the container, so anything it writes persists for the life of the instance. Copying the flag into a served directory makes it readable by anyone who can reach the instance, so remove it immediately after reading. The polluted attribute stays set and is evaluated on every product generation: leave it as an expression that returns a valid value of the expected type, or that code path raises for every later visitor. Do not point the injected command at configuration files or imported modules.

- status: proposed

## 2026-09-23 · git host with repo webhooks (BitHug / wily courier) · proposed

- source note: `solved/bithug.md`
- chain card: `knowledge/chains/pico-bithug-webhook-validate-before-template-ssrf-git-access-grant.json`
- verification: verified_live — the readme JSON returned by the live GET /_/<user>.git/api/readme contained the flag once access.conf had been pushed
- classified as: `web-ssrf` (score 3.5, 3 signals matched)
- also matched: `web-ssti` (2.5), `web-logic-flaw` (2.0), `web-race-condition` (1.5)
- signals that fired: 127.0.0.1, SSRF, webhook

**Confirming probe that worked**

> store a webhook whose URL is entirely a template placeholder, then trigger it with a ref that expands to a host and port the validator would have rejected

Expected: the stored URL is accepted despite expanding to a forbidden port, and the target records the request

Falsifier: the save is rejected, or the placeholder is not expanded at fire time

**Traps recorded on this solve**

- the handout is a plain tar despite a .tgz name, so tar tzf fails and looks exactly like a truncated download; check file before re-downloading
- the same formatString rewrites the BODY as well as the URL, so a binary payload containing {{ is silently corrupted
- git rejecting the pushed ref does not stop the webhook: the helper resolves on stdout close regardless of exit code
- build the packfile locally and replay it into a throwaway bare repo with git receive-pack --stateless-rpc before sending it anywhere

**Blast radius**: the challenge issues each user their own target repository and asks that you not touch anyone else's; register your own account and aim every payload at your own _/<user>.git. The push writes a new ref into that repo only.

- status: proposed

## 2026-09-24 · Nomad Notes · proposed

- source note: `solved/htb-nomad-notes-replace-pattern-nonce-reuse-referrer-exfil.md`
- chain card: `knowledge/chains/htb-nomad-notes-replace-pattern-nonce-reuse-referrer-exfil.json`
- verification: verified_live — the listener received the navigation with the full victim URL, including the flag parameter, in the Referer header
- classified as: `web-ssrf` (score 3.5, 3 signals matched)
- also matched: `web-xss` (2.5), `web-xs-leaks` (2.0), `web-ssti` (1.5)
- signals that fired: headless, localhost, render

**Confirming probe that worked**

> request the templated page with the user field set to a single $-backtick and read the raw response

Expected: the line is duplicated: the text preceding the placeholder (including anything already substituted, such as a nonce) appears inside the value

Falsifier: the two characters come back literally, meaning the renderer does not use String.replace with a string pattern

**Traps recorded on this solve**

- a free tunnel that shows an abuse interstitial keys on USER-AGENT, so it silently swallows every request a headless browser makes - navigation, script src and images alike. A curl smoke test passes and misleads you into reading 'no callback' as 'exploit failed'. Always re-test the listener with a browser User-Agent before trusting a negative result.
- the default referrer policy is strict-origin-when-cross-origin, which drops path and query - without a referrer meta set to unsafe-url the callback arrives with only the origin and no secret
- Express 5 leaves req.body undefined when no body parser matched, so a fetch without a content-type makes a destructuring handler throw 500 and the chain dies silently; have the payload report the response status back to the listener to find this
- script.src is a TrustedScriptURL sink, so under require-trusted-types-for it throws unless a policy is created; navigation is not a Trusted Types sink, which makes the meta-refresh route the robust one
- an arrow function cannot survive an escaper that strips angle brackets - use function(){} instead
- the reflecting placeholder may sit inside a title element, whose contents parse as text: open with a title end tag or the injected markup is inert

**Blast radius**: negligible. The application has no datastore, no session and no upload - the only side effect is launching a short-lived headless browser per request, and nothing persists between runs. There is nothing to clean up afterwards.

- status: proposed

## 2026-09-26 · Interstellar · confirmed

- source note: `challenges/Interstellar/challenge/src/communicate.php`
- chain card: `knowledge/chains/htb-interstellar-parseurl-curl-host-confusion-ssrf-localhost-edit-stored-proc-sqli-outfile-rce.json`
- verification: verified_live — Live HTB instance. The dropped file returned uid=33(www-data) gid=33(www-data) groups=33(www-data), ls / showed a single <hex>_flag.txt at the root, and cat of it returned the flag in the HTTP response body. Recorded in challenges/target-31236/state.json through tools/hooks.py post-probe (confirms, evidence-kind class then impact) and pre-flag (source live-response). Cleaned up afterwards: name reset and the file removed (404).
- classified as: `web-ssrf` (score 2.32, 4 signals matched)
- also matched: `web-race-condition` (1.17)
- signals that fired: 127.0.0.1, curl, render, url=

**Confirming probe that worked**

> POST /communicate.php with url=0://127.0.0.1:80;motherland.com:80/ and data[action]=edit&data[new_name]=ZZTESTZZ, then GET /

Expected: GET / renders 'Yo, ZZTESTZZ' — the host-confusion reached loopback AND the REMOTE_ADDR-gated edit accepted the request, proving both the SSRF and the pivot in one shot

Falsifier: 'Wrong URL!' (the suffix regex is anchored or compares the whole host), 'Failed when parsing URL!' (filter_var rejected the scheme/host shape -- retry under a junk scheme), or the name is unchanged, which means either curl did not stop at 127.0.0.1 or the fetch does not forward your session cookie, in which case index.php answers the login redirect instead of running the edit.

**Traps recorded on this solve**

- parse_url strips the port into its own key, so a :port in the submitted URL never reaches curl when only ['host'] is forwarded. An early port sweep across 1/22/80/3306/8080 that returns identical timeouts is measuring nothing -- the port was discarded before curl saw it.
- 0://[::ffff:127.0.0.1].motherland.com:80/ passes both gates and connects, but every port times out with 0 bytes: curl takes the bracketed IPv6 literal and nothing answers it in this container. 0://[127.0.0.1].motherland.com/ does reach loopback but Apache answers 400 because the Host header becomes '[127.0.0.1].motherland.com'. Both look like a working SSRF; only the semicolon form yields a usable request.
- the REMOTE_ADDR check is a STRICT allowlist -- index.php:45 is  if ($_SERVER['REMOTE_ADDR'] != '127.0.0.1')  -- so the origin must be exactly 127.0.0.1. Public writeups describe it as a blocklist that bans 127.0.0.2 and lets every other loopback address through; that is wrong, and believing it makes ::1 and 127.0.0.2 look like valid alternatives when neither passes. This was corrected against the handout after the solve.
- filter_var(FILTER_VALIDATE_URL) is stricter for http:// than for an unknown scheme: percent-encoded and bracketed hosts rejected under http:// are accepted under 0://. If a host shape is rejected, retry it with a junk scheme before discarding it. filter_var runs FIRST (communicate.php:11) and the host regex second (communicate.php:13), which is why the two error strings identify which gate you are against.
- the visible Key and Value inputs are not the wire format -- js/sendForm.js rewrites them to data[<key>]=<value> and communicate.php:19 runs http_build_query($data). Probing with key=/value= still exercises the URL gate, so URL findings stay valid, but the SSRF body does nothing until the array shape is used.
- CURLOPT_TIMEOUT is 1 second (communicate.php:24), so every server-side request has a one-second budget; a 'timed out after ~1000ms with 0 bytes' error says nothing about whether the target exists.
- the injection is SECOND ORDER: the write returns nothing useful and the SQL only runs on the next GET /. A payload that looks inert on submission is already armed.
- do not spend probes hunting for a reflected column: index.php:33 renders the name from the session and index.php:31 maps planet through pick_emoji(), so the channel is the page length (about 4650 bytes valid vs 72 on a SQL error).

**Blast radius**: Step 7 WRITES a PHP file into the webroot as the mysql user and gives command execution as www-data; pick a unique filename, because INTO OUTFILE refuses an existing path and a second trigger then only produces SQL errors. The injected name persists in the database and re-runs on EVERY page view until it is reset, so the app stays broken until step 8. Everything before step 7 touches only your own row. The SSRF itself is a blind-ish POST to loopback with a 1s curl timeout.

- the pivot needs TWO things: `data[]` becomes the POST body via `http_build_query()`, and communicate.php:16-23 forwards the caller's own `Cookie: PHPSESSID=$sessCookie`. That forwarded cookie is why the internal edit lands on the ATTACKER's row. When a server-side fetch forwards your credentials, the SSRF is an authenticated request as you.
- status: confirmed

## 2026-09-26 · ScreenCrack · confirmed

- source note: `challenges/ScreenCrack/challenge/app/Http/Controllers/SiteShotController.php`
- chain card: `knowledge/chains/htb-screencrack-domain-loopback-ssrf-gopher-redis-laravel-queue-forge-system-injection.json`
- verification: verified_live — Live HTB instance. GET /src/<uuid>.txt after the gopher probe contained '+PONG' and the full INFO server block (redis_version 7.0.15). LRANGE showed the genuine App\Jobs\rmFile payload, the forged copy was RPUSHed onto laravel_database_queues:default, and after the worker's next wake GET /src/pwn7b.txt returned the flag. Recorded in challenges/target-31591/state.json through tools/hooks.py post-probe (confirms, evidence-kind class then impact) and pre-flag (source live-response).
- classified as: `web-ssrf` (score 2.72, 3 signals matched)
- also matched: `web-nosqli` (1.17)
- signals that fired: 127.0.0.1, SSRF

**Confirming probe that worked**

> POST /api/get-html with {"site":"gopher://<a domain that resolves to 127.0.0.1>:6379/_%2A1%0D%0A%244%0D%0APING%0D%0A%2A1%0D%0A%244%0D%0AQUIT%0D%0A"}, then GET the returned /src/<uuid>.txt

Expected: the saved file contains +PONG — the host filter was bypassed by a name, the scheme was never checked, and the QUIT trailer made the reply readable

Falsifier: 'Dont do naughty stuff.' (the validator resolves domains too, or rejects non-http schemes), or {'status':'failed'} with no file even with QUIT present (curl has no gopher support, or nothing is listening on 6379)

**Traps recorded on this solve**

- count the class-name length by hand and then check it against a real payload. This solve first pushed O:22:"App\Message\FileQueue" -- the name is 21 bytes -- so PHP's unserialize rejected it and the job silently did nothing. The mistake was invisible until LRANGE showed the app's own payload spelling it O:21. When a serialized payload has a producer you can observe, read its output before writing your own.
- without a trailing QUIT the gopher SSRF reports {'status':'failed'} and returns no filename, because redis keeps the connection open until curl's 3s CURLOPT_TIMEOUT expires and curl_errno makes the handler bail. That failure is indistinguishable from 'gopher is unsupported' and will send you looking for a different protocol.
- the queue key carries Laravel's redis prefix. With no APP_NAME in .env the default is Str::slug('Laravel','_').'_database_', so the list is laravel_database_queues:default, not queues:default. Confirm with KEYS * through the same oracle rather than assuming.
- the worker is started with --sleep=600, so a pushed job may wait ten minutes before running. A silent queue is not evidence that the payload is wrong -- check LLEN and the :reserved zset to see whether the worker has consumed anything at all before changing the payload.
- validateUrl runs BEFORE getSS prepends http://, so a bare host like example.com fails validation on the screenshot endpoint (parse_url returns no host). Only fully-qualified URLs get through, on either endpoint.
- isValidDomain calls checkdnsrr, so the chosen name must actually resolve from inside the container. Pick a name whose loopback mapping is public rather than one you control by hosts-file or local resolver.

**Blast radius**: The SSRF writes one file per request into /www/public/src, which the app's own rmFile jobs would eventually clean. The RCE runs as the worker user and this solve used it additively: cat /flag into a new file under the webroot, read it over HTTP, then queued a second job to delete both that file and the 'halo' file the sink appends to. Note the queue is shared application state: a malformed forged payload stays in the list and makes the worker throw on every wake until it is drained or retried out. Do NOT reach for the redis CONFIG SET dir + dbfilename + SAVE trick here -- it rewrites the live RDB and the server's persistence settings for a target that already yields clean RCE through the queue.

- status: confirmed
