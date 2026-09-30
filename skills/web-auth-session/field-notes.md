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

## 2026-09-27 · Nexus Void · confirmed

- source note: `challenges/Nexus Void/web_nexus_void/Nexus_Void/Middleware/JWTMiddleware.cs`
- chain card: `knowledge/chains/htb-nexusvoid-jwt-middleware-no-return-claim-sqli-jsonnet-typenamehandling-process-setter-rce.json`
- verification: verified_live — Live HTB instance. Controls: no cookie -> 302, Token=garbage -> 302, Token=a.b.c -> 302; an alg=none token with an empty signature -> 200 rendering id="username" value="n0ne_f0rged". The planted gadget answered 200 Added, the trigger GET answered 200, and GET /nv_9f21.txt returned the flag. Recorded in challenges/nexusvoid/state.json through tools/hooks.py post-probe (confirms, evidence-kind class then impact) and pre-flag (source live-response). The dropped file was removed with a second gadget and verified 404; the probe items were removed from the wishlist and the page shows 'Wishlist is empty'.
- classified as: `web-auth-session` (score 1.13, 1 signals matched)
- also matched: `web-parser-differential` (1.09), `web-open-redirect` (0.49)
- signals that fired: alg

**Confirming probe that worked**

> GET /Home/Setting three times: with no Cookie header, with Token=garbage, and with Token=<base64url {"alg":"none","typ":"JWT"}>.<base64url {"username":"n0ne_f0rged","ID":"1","iss":"NexusVoid"}>. (trailing dot, empty signature)

Expected: the first two answer 302 to /, the third answers 200 and the page contains id="username" value="n0ne_f0rged" -- a username that belongs to no account

Falsifier: the forged token also answers 302, or the no-cookie request also answers 200 (the page was never gated, so the 200 says nothing)

**Traps recorded on this solve**

- the wrong first move here is attacking the HS256 key, and it is an expensive one: 14,448,372 candidates from SecLists scraped-JWT-secrets.txt and rockyou.txt produced no match. The token looks like a signing problem and is not one -- the signature is never checked, so no key search can succeed. Read the middleware before touching the crypto.
- there is no admin surface to reach by impersonation, so do not go looking for one. /Home/Market, /Home/Trending, /Home/Collection, /Home/Wallet, /Home/Admin, /Home/Dashboard, /Home/Profile, /Home/Orders, /Home/Seller, /Home/Flag and /Admin all answer 404, although the nav bar lists market, trending, collection and wallet. Forging username=admin, administrator, root or Xclow3n changes nothing but the echoed string: the three real pages differ only by the length of the username. The privilege is in how far the ID claim reaches into SQL, not in the name.
- the wrong first move here is attacking the HS256 key. The token looks like a signing problem and it is not one: the signature is never checked, so a key search is wasted no matter how long it runs. Read the middleware before touching the crypto.
- `ValidateToken` returns `false.ToString()`, which is "False" with a capital F, and the caller compares it to "false". Even if the caller had returned, the comparison would never match. Two independent bugs on adjacent lines, and only reading both explains why an invalid token is accepted.
- the redirect still happens, so a browser and any client that follows redirects will land on the login page and hide the bypass. Use a client that does not follow redirects, and read the body that came back WITH the 302.
- in the product lookup, `sellerName` injected with OR makes FirstOrDefault return the first row of the whole table, so the response says "Added" while a product you never named is what got added. A boolean oracle built on that endpoint must use AND, not OR.
- the boolean oracle is 200 versus 500, not two different messages: a FALSE lookup returns null and the next line dereferences product.name, so the app throws. The 500 is the FALSE branch, not a broken probe.
- the INSERT branch is reachable only while the ID owns no Wishlist row. Plant one payload per fresh ID; re-using an ID silently takes the UPDATE branch, where the data column is generated and not yours.
- GET /Home/Wishlist reads `WHERE ID='{ID}'` (quoted) while POST reads `WHERE ID={ID}` (unquoted). The same claim is injectable in one and not the other, so check every statement rather than assuming the quoting is consistent.
- WishlistRemove ends in RedirectToAction("Home", "Wishlist"), which has the action and controller the wrong way round and answers 404. The removal SQL has already run by then, so a 404 there is success, not failure.
- tools/classify.py --source on a .NET handout reads bin/ and obj/, so it reports matches inside compiled .dll and .a files with meaningless line numbers. Read the Controllers, Helpers and Middleware directories yourself; the classifier's white-box output is unusable on a published .NET tree until those directories are skipped.

**Blast radius**: Every step writes. The planted row is an INSERT at an ID no real account holds yet, so it displaces nothing, but it CANNOT be removed with the same primitive: the INSERT branch only runs when the ID owns no row, so a second attempt at that ID takes the UPDATE branch instead. Pick a high ID (1337 here), use one row per payload, and expect them to stay. The command runs as root, so keep it to a copy into wwwroot and remove that file afterwards with a second one-line gadget -- verified 404 after. Anything added to your own wishlist during probing is removable through /Home/WishlistRemove. Do not use `OR '1'='1'` in the product lookup on a shared instance without expecting it: FirstOrDefault then returns the FIRST product in the table, not the one you named, and that product is what gets added.

- status: confirmed

## undated · Desire · confirmed

- source note: `solved/desire.md`
- chain card: `knowledge/chains/htb-desire-session-file-path-traversal-via-username-cookie.json`
- verification: verified_live — GET /user/admin returned 200 and admin.html line 229 carried HTB{...}; the body was saved to /home/kali/ctf-work/challenges/web30732/artifacts/admin_response.html and recorded through tools/hooks.py post-probe (evidence-kind class) then pre-flag --source live-response
- classified as: `web-auth-session` (score 0.0, 0 signals matched)
- also matched: `web-parser-differential` (1.09)
- filed by operator override: the matcher did not rank this class; the chain is filed under the class whose first probe opens it

**Confirming probe that worked**

> Log in normally, then repeat one authenticated request with the plaintext username cookie replaced by a string that is not a registered account (for example nosuchuser_zzz), and again with the session cookie replaced by a single junk character.

Expected: the junk session cookie is accepted while the unknown username returns a server error. That asymmetry says the identity is the plaintext cookie and that it is dereferenced server-side, which is what makes it a candidate path component.

Falsifier: tampering with the username cookie changes nothing, or the session cookie is verified (a junk value is rejected) -- then the identity is the token and this card does not apply.

**Traps recorded on this solve**

- mholt/archiver v3.5.0 SILENTLY SKIPS a zip entry whose name escapes the destination: the response is a normal 202 and nothing is written. The tell is that re-uploading the same escaping entry never produces the 'file already exists' error that a clean entry produces on its second upload. Read that asymmetry as the patch, not as the vulnerability -- the traversal here is in the SESSION path, not in the archive.
- Because the extractor refuses to overwrite, the 'file already exists: <path>' error is a clean file-existence oracle -- but only inside the destination. Escaping probes always answer 202, so a sweep for files at the application root reads as 'nothing is there' whatever is actually there. Run a control on a path you know exists before trusting one of those sweeps.
- A username cookie the application cannot resolve gives Fiber's bare 'Internal Server Error', while the handler's own failures give JSON. The two 500s mean different things: the bare one is the redis lookup missing, so it also confirms that the cookie is the key.
- sessionID is sha256 of the SERVER's clock in whole seconds. One candidate hash is a coin flip; put the hashes for a few seconds either side of the login into the same archive and the race disappears.
- The registration filter blocks / . and \ in the username, which makes the account name look safe and hides that the same value travels back as an unvalidated cookie. Check the cookie separately from the field that set it.
- FLAG is an environment variable (ENV FLAG= in the Dockerfile), not a file, so no amount of arbitrary file WRITING reaches it directly -- the only route is to satisfy the Role == "admin" test that guards the template.
- mholt/archiver v3's Zip.CheckPath is a STRING prefix test, not a path-boundary test: to,_ = filepath.Abs(to); if !strings.HasPrefix(filepath.Join(to, filename), to). An entry named ../<username>ZZ/f therefore resolves to a SIBLING directory that still shares the prefix and IS written -- measured here as 'reading file in zip archive: file already exists: files/probe_sess_9k2xZZ/px.txt'. A plain ../f is skipped and a sibling-prefix ../<username>ZZ/f is written, which is why one negative on the plain form does not close the class.
- A zip SYMLINK entry (external_attr 0o120777<<16) is honoured by extractFile -> writeNewSymbolicLink, and its name only has to satisfy the same prefix test. Planting ../<username>S with content '/' makes every absolute path reachable as ../<username>S/<abs> -- measured as 'file already exists: files/probe_sess_9k2xS/etc/passwd'. writeNewSymbolicLink also os.Remove()s whatever is already at that name, which is the ONE way to overwrite despite OverwriteExisting=false, and it is destructive on a shared instance.
- The username cookie needs an entry in REDIS, not a row in the SSO database: /register rejects / . and \ so no account can ever carry a dot segment, and probing the cookie alone reads as 'must be an existing user'. PrepareSession (http.go:73-75) writes redis[username] before the password is checked, so a deliberately failed login mints the key for any string at all. Measuring the cookie without also reading the login handler closes the real bug by mistake.

**Blast radius**: Registration and the archive upload both write, and neither the Go service nor the Node SSO exposes a delete route, so every account and every extracted file stays on the shared instance. Use one throwaway account and one small archive. The forged session file lands in YOUR OWN files/<account>/ directory, so nobody else's session is touched, and the redis key written by the wrong-password login is the traversal string rather than a real username -- it cannot log anyone else out. archiver refuses to overwrite an existing file, so a repeat upload of the same entry name fails with 500 rather than corrupting anything.

- status: confirmed
