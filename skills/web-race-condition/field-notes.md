# Field notes — Race condition / TOCTOU

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

## 2026-09-07 · ApexSurvive · proposed

- source note: `solved/apexsurvive.md`
- chain card: `knowledge/chains/htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce.json`
- verification: verified_live — flag rendered in the page by the overwritten template
- classified as: `web-race-condition` (score 2.5, 2 signals matched)
- also matched: `web-xss` (4.5), `web-ssti` (3.5), `web-file-upload` (2.5)
- signals that fired: race condition, verification token

**Confirming probe that worked**

> send two interleaved profile updates and observe which address receives which token

Expected: a token belonging to one address arrives at the other

Falsifier: the token is read inside the same transaction as the update

**Traps recorded on this solve**

- a partial configuration overwrite loses the socket and bricks the instance permanently
- a trigger file that gets imported on reload must be valid code; a PDF placed there bricks the worker
- the HTML sanitiser escapes ampersands in stored text, so query strings must be built at runtime
- base64url decoding in the browser fails without manual padding
- the bot re-logs in per visit, so stolen cookies expire quickly; verify immediately

**Blast radius**: overwriting server configuration or an imported module can permanently break the instance

- status: proposed

## 2026-09-23 · ApexSurvive · proposed

- source note: `solved/apexsurvive.md`
- chain card: `knowledge/chains/htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce.json`
- verification: verified_live — flag rendered in the page by the overwritten template. Re-verified live 2026-09-23 on a second instance: the race unlocked isInternal at round 2 (token ee8927bd, 45/45 requests 200), the admin cookie decoded to {'id': 1, ...} with /challenge/settings returning 200, and the overwritten template rendered the flag on the first poll of /challenge/product/1 with no reload forced.
- classified as: `web-race-condition` (score 2.5, 2 signals matched)
- also matched: `web-xss` (4.5), `web-file-upload` (3.5), `web-ssti` (3.5)
- signals that fired: race condition, verification token

**Confirming probe that worked**

> send two interleaved profile updates and observe which address receives which token

Expected: a token belonging to one address arrives at the other

Falsifier: the token is read inside the same transaction as the update

**Traps recorded on this solve**

- A partial configuration overwrite loses the socket and bricks the instance permanently — and the re-solve proved this step is not needed at all.
- A trigger file that gets imported on reload must be valid code; a PDF placed there bricks the worker.
- The HTML sanitiser escapes ampersands in stored text, so query strings must be built at runtime.
- base64url decoding in the browser fails without manual padding.
- The bot re-logs in per visit, so stolen cookies expire quickly; verify with an authenticated page immediately.
- Restoring the overwritten template does not un-cache it: workers that already cached the malicious version keep serving it until the instance restarts. Say so rather than assuming the write was undone.
- The input sanitiser may cover request.args and request.form but not request.files, so an uploaded filename reaches os.path.join unfiltered.
- The handed-over host:port may speak TLS; a plain http request answering '400 The plain HTTP request was sent to HTTPS port' is the tell.

**Blast radius**: overwriting server configuration or an imported module can permanently break the instance

- status: proposed
