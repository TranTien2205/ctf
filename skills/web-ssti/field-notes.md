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
