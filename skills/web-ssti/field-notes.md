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

## 2026-09-18 · Site still under construction · proposed

- source note: `solved/const-flask.md`
- chain card: `knowledge/chains/htb-const-flask-jinja2-lipsum-rce.json`
- verification: verified_live — popen cat flag.txt returned HTB{t3mpl4t3s_4r3_m0r3_p0w3rfu1_th4n_u_th1nk!} rendered inside the str() call output
- classified as: `web-ssti` (score 4.5, 4 signals matched)
- also matched: `web-ssrf` (2.5), `web-file-upload` (1.5), `web-race-condition` (1.5)
- signals that fired: 49, jinja, template, {{

**Confirming probe that worked**

> GET /{{7*7}}

Expected: the custom 404 template renders <str>49</str>

Falsifier: the raw payload is escaped or filtered, or the page shows a different 404

**Traps recorded on this solve**

- a slash in the payload breaks the route pattern (<str> does not match slashes); slash-free shell commands are the easy route
- {{config}} and environ list only environment sections, not the flag
- the lipsum.__globals__ namespace gives os and any module without needing a real subconversation

**Blast radius**: arbitrary python execution as root inside the single-container app

- status: proposed
