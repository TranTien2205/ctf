# Field notes — Server-side template injection

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

## 2026-09-12 · Neonify · proposed

- source note: `solved/neonify.md`
- chain card: `knowledge/chains/htb-neonify-erb-ssti-newline-filter-bypass.json`
- verification: verified_live — flag returned inside the glow span from the live endpoint
- classified as: `web-ssti` (score 3.5, 3 signals matched)
- also matched: `web-race-condition` (1.5), `web-auth-session` (1.5), `web-ssrf` (1.5)
- signals that fired: <%=, erb, template

**Confirming probe that worked**

> POST / with neon=abc\n<%= 7*7 %>

Expected: the glow output renders 49

Falsifier: the filter blocks the payload unchanged or returns literal unrendered text

**Traps recorded on this solve**

- puts inside eval goes to server stdout, not into the template output
- the benign line must satisfy the per-line charset check
- encode payload internals with base64 because parentheses, quotes and dots are blocked

**Blast radius**: read-only primitive; no shared-state writes observed, only file reads on the challenge instance

- status: proposed

## 2026-09-24 · Bobby's Bistro · proposed

- source note: `solved/htb-bobbys-bistro-sqli-jwks-overwrite-chameleon-ssti.md`
- chain card: `knowledge/chains/htb-bobbys-bistro-sqli-jwks-write-chameleon-ssti.json`
- verification: verified_live — the rendered announcement stored and displayed on the listing page contained the file contents inside the div emitted by the template directive
- classified as: `web-ssti` (score 3.5, 3 signals matched)
- also matched: `web-auth-session` (3.5), `web-file-upload` (2.5), `web-sqli` (2.5)
- signals that fired: ${, Template, Template(

**Confirming probe that worked**

> submit a tautology in the field that is interpolated into the filter and count the rows rendered by the view

Expected: every row of the table comes back instead of one, exposing whichever columns the template prints

Falsifier: a single row or an error, meaning the value really is bound as a parameter

**Traps recorded on this solve**

- a character blacklist is not a sandbox: chr() concatenation rebuilds any string once quotes and dots are stripped, and an iterating directive avoids the method call the blacklist was aimed at
- the blacklist ran on template INPUT only, so characters it strips can still appear in the OUTPUT - the recovered value kept its own braces
- replacing the key set rather than appending to it is destructive on a shared instance and also needlessly noisy; keep the original entry and put the original file back when done
- the view template decides what the injection can read - check which columns are actually printed before assuming a column is reachable
- the resident bot here is a plain requests session, not a browser, so there is no client-side attack surface against it despite it holding the privileged account
- uploads and generated rows cannot be removed afterwards; prove primitives with throwaway names and build payloads offline

**Blast radius**: mostly additive and reversible, but read this before firing. The injection is SELECT-only. The key set gains one extra key: APPEND, never replace, or every other player's session breaks, and restore the original afterwards. The uploaded probe file and the rendered announcement row cannot be deleted - there is no delete endpoint - and the announcement is written once per registered user, so whatever the template prints becomes visible to everyone on the instance. Develop the template payload locally first instead of iterating against the shared target.

- status: proposed

## 2026-09-27 · Jerryboree · confirmed

- source note: `challenges/JerryTok/web_jerrytok/challenge/src/Controller/DefaultController.php`
- chain card: `knowledge/chains/htb-jerryboree-twig-ssti-symfony-fragment-filesystem-write-htaccess-cgi-escape.json`
- verification: verified_live — Live HTB instance. /?location={{7*7}} rendered 49; a written probe reported SAPI=cgi-fcgi, disable_functions covering the exec family, open_basedir pinned to the app root and an empty LD_PRELOAD; the dropped .rick script returned the flag in the HTTP response body. Recorded in challenges/jerrytok/state.json through tools/hooks.py post-probe (confirms, evidence-kind class then impact) and pre-flag (source live-response). All six dropped files removed afterwards and verified 404. Cleanup: Filesystem::remove over the six paths; / still answers 200.
- classified as: `web-ssti` (score 2.01, 3 signals matched)
- also matched: `web-ssrf` (0.95)
- signals that fired: 49, template, {{

**Confirming probe that worked**

> GET /?location={{7*7}} and then GET /?location={{_self}}

Expected: the page renders 49 in place of the value, and _self renders __string_template__ followed by a hash: the parameter is compiled as template source

Falsifier: the braces come back literally (the value is passed as context, not source), or the page 500s on every brace (the template is not compiled from the request at all)

**Traps recorded on this solve**

- measure the jail, do not read it off the Dockerfile. This image sets LD_PRELOAD to a GNU libiconv build, which is the precondition for the well-known iconv memory-corruption bypass, but at runtime getenv('LD_PRELOAD') is EMPTY. Believing the Dockerfile would have sent the solve into a heap-grooming exploit that could not have worked.
- the shipped document root contains a file named .htacess, one letter short of .htaccess, so Apache never reads it. It is not a rewrite config that is failing, it is an inert file and the real .htaccess slot is free. Check the spelling before concluding overrides are disabled.
- ScriptAlias /cgi-bin /usr/bin looks like the way in and is a dead end on its own: a request to a real binary returns 500 and a request to a missing one returns 404, so execution IS happening, but Apache discards the output because a plain binary emits no CGI headers. Query-string-to-argv also did not fire here (a program written through awk left no file), so neither output nor arguments were reachable that way.
- Twig 3.24 rejects a string where a filter expects a callable, so map/filter/sort/reduce with 'system' all fail. Fingerprint the engine first with constant('Twig\\Environment::VERSION') instead of cycling payloads.
- source() and include() on an absolute path answer 500 here, and it is open_basedir rather than the Twig loader; do not read that as the injection being sandboxed.
- a CGI script must print Content-Type and a blank line before anything else, and it must be chmod 0755. Either one missing gives the same opaque 500 as a failed exec.

**Blast radius**: Steps 4 and 5 WRITE into the document root, and the .htaccess changes how Apache treats that directory for everyone until it is removed. Keep the dropped files to a private extension, and remove every one of them afterwards through the same Filesystem::remove gadget; this solve verified 404 on each dropped path and 200 on / afterwards. The command itself is only the challenge's own read-only helper. Do not leave the .htaccess behind: it enables CGI execution for the whole directory.

- status: confirmed
