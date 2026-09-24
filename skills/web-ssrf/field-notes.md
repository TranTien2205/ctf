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
