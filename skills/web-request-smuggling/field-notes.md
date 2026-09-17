# Field notes — Request smuggling / CRLF injection

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

## 2026-09-11 · Weather App · proposed

- source note: `solved/weather_app.md`
- chain card: `knowledge/chains/htb-weather-app-ssrf-crlf-request-smuggling-upsert.json`
- verification: verified_live — flag returned in the login response
- classified as: `web-request-smuggling` (score 4.5, 4 signals matched)
- also matched: `web-ssrf` (4.5), `web-sqli` (3.5), `web-ssti` (2.5)
- signals that fired: Content-Length, \u010D, crlf, http://${endpoint}

**Confirming probe that worked**

> put a harmless marker with one folded space character into the interpolated field and compare the error with an ordinary hostname

Expected: the parser accepts the folded character, showing the field is not encoded

Falsifier: the field is encoded or validated, so no control characters survive

**Traps recorded on this solve**

- the injected content length must count the body bytes exactly
- a trailing request fragment is needed so the smuggled request is terminated

**Blast radius**: the upsert changes an existing account's password on a shared instance; other players lose access to that account

- status: proposed
