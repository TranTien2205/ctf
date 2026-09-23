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
