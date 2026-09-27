# Field notes — Authentication and session

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

## 2026-09-18 · broken authentication · proposed

- source note: `solved/broken-authentication.md`
- chain card: `knowledge/chains/htb-broken-authentication-unsigned-base64-json-cookie-forge.json`
- verification: verified_live — the flag was read from the body of GET / on the live target, inside an <h1> element, with the forged cookie attached
- classified as: `web-auth-session` (score 2.5, 2 signals matched)
- also matched: `web-race-condition` (1.5), `web-ssti` (1.5), `web-parser-differential` (1.5)
- signals that fired: eyJ1c2VybmFtZSI6ImN0ZnByb2JlX2ExIn0, phpsessid

**Confirming probe that worked**

> register your own account, log in, then URL-decode and base64-decode the session cookie returned by Set-Cookie

Expected: the decoded bytes are readable structured data containing the username you just chose

Falsifier: the value is opaque, or a signature or MAC segment travels with it and the server rejects an edited value

**Traps recorded on this solve**

- the cookie name lies: PHPSESSID here carried base64 JSON, not a PHP session id, so do not skip decoding because the name looks standard
- curl writes the cookie URL-encoded; %3D must be decoded to = before base64 decoding or the decode looks like it failed
- re-encode with base64 -w0, since a wrapped line breaks the header

**Blast radius**: one self-registered user row on a shared challenge database. The forge itself is a read with a chosen cookie and mutates nothing. Do not spray usernames; register once and reuse that account.

- status: proposed

## 2026-09-18 · broken authentication control (TODO OR NOT TODO) · proposed

- source note: `solved/htb-todo-or-not-todo-list-all-access-control.md`
- chain card: `knowledge/chains/htb-todo-magic-list-all-segment-access-control-bypass.json`
- verification: verified_live — the flag was returned as the name field of one object in the JSON array from the listing endpoint on the live target
- classified as: `web-auth-session` (score 1.5, 1 signals matched)
- also matched: `web-cache-poisoning` (1.0), `web-logic-flaw` (1.0), `web-xxe` (1.0)
- signals that fired: session

**Confirming probe that worked**

> issue the listing request twice with one cookie and one secret, once for your own identity and once with the identity segment replaced by the collective value

Expected: your own listing is empty or short while the collective value returns rows owned by another account

Falsifier: the collective value returns the same rows as your own identity, or is rejected with the same error as an unrelated identity

**Traps recorded on this solve**

- the session cookie, the identity and the per-session secret are issued together on each visit; pairing a stale identity with a fresh cookie returns an authorisation error that looks exactly like the control working, which is a false negative that can kill a correct hypothesis
- capture the cookie, the identity and the secret from one single response before probing
- the session cookie is signed and does not need to be forged; the bug is entirely in the path segment

**Blast radius**: read-only. Use the listing route only; the same API exposes completion and deletion routes that take an id and would mutate another account's objects, so never point those at an id that is not yours.

- status: proposed

## 2026-09-23 · NeuroSync · proposed

- source note: `solved/htb-neurosync-next-middleware-bypass-curl-ssrf-gopher-redis-signed-osexec.md`
- chain card: `knowledge/chains/htb-neurosync-next-middleware-bypass-curl-ssrf-gopher-redis-signed-osexec.json`
- verification: verified_live — GET /api/bci/analytics returned 401 plain and the analytics payload with the subrequest header; pointing sourceUrl at the log endpoint with a doubled-dot path returned the HMAC key base64-encoded; after the signed queue entry, reading the payload's output file back through the same endpoint returned the flag base64-encoded. After cleanup that path no longer exists and the endpoint serves normal analytics again.
- classified as: `web-auth-session` (score 1.5, 1 signals matched)
- also matched: `web-race-condition` (2.5), `web-ssrf` (2.5), `file-read-primitives` (2.5)
- signals that fired: HS256

**Confirming probe that worked**

> Request a protected API route twice, once plain and once carrying the framework's internal-subrequest header with the middleware name repeated to the recursion limit.

Expected: 401 without the header and the route's real response with it, proving the middleware layer is skipped rather than satisfied.

Falsifier: Both requests return 401, meaning the version is patched or the header name is wrong, and the API has to be reached with a real token instead.

**Traps recorded on this solve**

- A gopher request to a datastore never returns, because the datastore does not close the connection and the outbound client has no timeout. The write has already happened: treat the client-side timeout as success and verify with a read, or append a quit command to the payload.
- RESP length prefixes are byte counts and must match the payload exactly.
- Both the file read and the flag arrive inside HTTP 500 bodies, never in a 200; a client that only parses successful responses sees nothing.
- execFile with an argv array is injection-proof, so shell metacharacter probes are wasted budget; the scheme is the degree of freedom.
- The worker signs the ENCODED payload, so the signature must be computed over the base64 text and not over the plaintext command.
- Worker output is discarded to a null log, so the payload has to write where the read primitive can reach.
- A filename randomised at boot has to be globbed, which is why the chain needs execution rather than the read alone.
- The Next 15 bypass header needs the middleware name repeated up to the recursion limit; a single occurrence does not trip it.

**Blast radius**: The executed command runs as root inside the container and the queue is shared, so anything pushed there runs once for whoever pops it. Copying a secret into a web-readable directory exposes it to every other visitor until removed. The stored sourceUrl is global process state: leaving it pointed at gopher or at a missing file breaks the endpoint for everyone, so restore it. A gopher request to a datastore that does not close the connection leaves the outbound client hanging with no timeout, which ties up a worker on the target.

- status: proposed

## 2026-09-26 · Intergalactic Bounty · confirmed

- source note: `challenges/Intergalatic Bounty/web_intergalatic_bounty/challenge/controllers/bountyController.js`
- chain card: `knowledge/chains/htb-intergalactic-bounty-recipient-array-differential-otp-mass-assign-needle-output-nunjucks-rce.json`
- verification: verified_live — Live HTB instance. GET /transmit returned HTTP 200 rendering the bounty JSON that needle had written over views/transmit.html, with the `status` field replaced by the output of `cat /flag.txt`. Recorded in challenges/galactic-bounty/state.json through tools/hooks.py post-probe (verdict confirms, evidence-kind impact) and pre-flag (source live-response).
- classified as: `web-auth-session` (score 1.08, 1 signals matched)
- also matched: `web-logic-flaw` (0.93)
- signals that fired: JWT

**Confirming probe that worked**

> POST /api/sendEmail with {"email":["<your registered address>@interstellar.htb","test@email.htb"]}, then GET the mail app on the second exposed port

Expected: HTTP 200 {"message":"New verification code sent"} and the verification code visible in the mailbox that only shows mail addressed to test@email.htb — proving the array was read as an IN-list by the ORM and as a recipient list by the mailer

Falsifier: the mailbox stays empty (nodemailer given a single recipient, or the lookup is a strict string equality that an array cannot satisfy), or /api/sendEmail answers 'User not found' (the ORM rejected the array instead of widening to IN)

**Traps recorded on this solve**

- needle's `output` alone CRASHES the app when the fetched response is JSON. With parse_response at its default 'all', needle emits a parsed object and then does file.write(chunk) on it: ERR_INVALID_ARG_TYPE escapes as an unhandled rejection because transmitAPI has no try/catch, node exits, supervisord restarts it and sequelize.sync({force:true}) wipes the database. Pollute parse_response:false in the same request. Reproduced offline against needle 3.3.1 before it was fired again.
- the PUT always answers 500 {"message":"Error fetching data"} — that is data.update() failing AFTER mergedeep has already run. The pollution has landed; do not read the 500 as a failed probe. Confirm it out of band with an unauthenticated request (once `cookies` is polluted, cookie-parser returns early because req.cookies is inherited, and every request authenticates as the polluted token).
- the puppeteer branch is a measured dead end on modern node. Object.prototype.debuggingPort DOES reach chromium's argv (computeLaunchArguments destructures it off the options object, and @puppeteer/browsers spawns with a plain {detached,env,stdio} literal), but node 20.18.3 ignores a prototype-inherited `shell` — an own shell:true shells out, the inherited one does not — so the argv injection never reaches /bin/sh. BrowserLauncher also existsSync()s executablePath, which kills the 'executablePath = command #' variant.
- nunjucks caches compiled templates per loader, so overwriting a view that has already been rendered in this process is silently a no-op. views/index.html is the obvious target and the wrong one if anything has fetched / — use a view no request has reached yet.
- JSON.stringify escapes the double quotes inside the payload, so the template on disk reads require(\"child_process\"). nunjucks' lexer unescapes it, but only if the OUTER quotes are single — write {{range.constructor('...\"...\"...')()}}, never the reverse.
- MailHog persists across an app restart (separate supervisord program, maildir storage), so after a crash the mailbox still holds the previous code. Hit /deleteall on the mail app before re-reading, or take the last match, or you will verify with a stale OTP.
- registerAPI's response says 'Verification email sent' but User.createUser never sends one. Only /api/sendEmail does. Waiting for the mail that the registration response promised wastes the first probe.
- the email-parser polyglot that public writeups use ('"test@email.htb ..."@interstellar.htb') is a different opener for the same step. A differential sweep of email-addresses 5.0.0 against nodemailer 6.9.16 over 25 candidate strings found no single-address form that parses as domain interstellar.htb while producing envelope recipient test@email.htb — the array shape goes through /api/sendEmail instead, which skips the domain check entirely.
- provenance: the chain was derived from the pinned package sources (needle's `output`, puppeteer's debuggingPort/shell) before any search; a writeup search was then used once, to choose between those two candidate final hops rather than spend probes on both, and the puppeteer branch was measured dead locally afterwards. Card is filed writeup-assisted for that reason.

**Blast radius**: Step 6 writes onto Object.prototype for the lifetime of the process and step 7 OVERWRITES a template file on disk — views/transmit.html stops being the real page until the instance is restarted. Pick a view that has not been rendered yet in that process: nunjucks' FileSystemLoader caches compiled templates by name, so overwriting a view that was already served does nothing. The PUT itself is safe for the row: mergedeep adds no own key to the target, so data.update() is a no-op update (it still answers 500, see traps). Anything that crashes the node process is expensive here because database.js runs sequelize.sync({force:true}) on boot: every account, bounty and the JWT signing secret are destroyed and the whole setup has to be redone.

- status: confirmed
