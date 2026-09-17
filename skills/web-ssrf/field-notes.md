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

## 2026-09-17 · DepotPrint · proposed

- source note: `solved/depotprint.md`
- chain card: `knowledge/chains/htb-depotprint-dupkey-gate-formatstring-supervisor-jwt.json`
- verification: verified_live — manifest depot-master-record note read from the rendered /console PDF on 192.168.223.1:9000
- classified as: `web-ssrf` (score 5.5, 5 signals matched)
- also matched: `web-auth-session` (2.5), `web-open-redirect` (2.0), `web-race-condition` (1.5)
- signals that fired: 127.0.0.1, Headless, render, ssrf, webhook

**Confirming probe that worked**

> GET /render.php?target=http://127.0.0.1:5000/status&target=https://example.com&label=D&note=x and read the produced PDF

Expected: the PDF contains the text 'depotprint render worker online'

Falsifier: both targets are rejected, or the PDF shows the external page only

**Traps recorded on this solve**

- the raw QUERY_STRING forwarding means percent-encoded bytes reach the worker unchanged; werkzeug decodes them once
- a stored {format} payload only explodes the NEXT time /queue is rendered, not at insert time
- Chrome percent-encodes braces in the displayed URL; the same_document comparison survives via unquote
- httpbin-style redirect chains die against same_document; the parser split does not need a redirector
- the PDF text layer is glyph-IDs mapped by ToUnicode; decode bfchar and bfrange or the text reads as garbage

**Blast radius**: arbitrary request forgery through a behind-the-gate chrome; the leaked signing key impersonates supervisors until the container restarts

- status: proposed
