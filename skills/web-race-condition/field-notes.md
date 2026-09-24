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

## 2026-09-23 · PhantomFeed · proposed

- source note: `solved/phantomfeed.md`
- chain card: `knowledge/chains/htb-phantomfeed-redos-verification-race-nuxt-open-redirect-oauth-token-xss-reportlab.json`
- verification: verified_live — HTTP 200 from GET /backend/static/zz.txt whose body was the flag copied out of /flag<random>.txt on the live target
- classified as: `web-race-condition` (score 2.5, 2 signals matched)
- also matched: `web-ssti` (4.5), `web-auth-session` (3.5), `web-oauth-sso` (3.5)
- signals that fired: gether when the regex ends, and one of them reads the row be, redeem

**Confirming probe that worked**

> POST /phantomfeed/register with email=a@ + 26 a + ! , timed against a normal email

Expected: the registration takes several seconds against a baseline near one second, and the cost roughly doubles for each extra character

Falsifier: the timing is flat with input length, so the validator does not backtrack and the window does not exist

**Traps recorded on this solve**

- the race cannot be won by timing one request: the regex holds the interpreter lock, so an expensive request is starved for the whole window and served only after the disabling update commits
- a longer backtracking payload makes it worse, because the reverse proxy returns a gateway timeout at sixty seconds
- a client-side router redirect returns 200 with no Location header, so it cannot be confirmed from the response
- the JSON serialiser in the reflection escapes double quotes and backslashes, so the injected script must avoid both
- the template engine escapes the payload's quotes and angle brackets, but the PDF parser decodes character references in the attribute, so no bypass is needed and no unescaping should be attempted
- the export route returns early when the collection is empty, so a record has to be created first
- a detector that assumes no digits between a field name and its value fails, because escaped quotes render as numeric character references

**Blast radius**: steps 3 and 9 write. The race leaves one extra account per attempt, so keep the attempt count low. The export payload runs a shell command as the application user: copy the flag to a new path, never overwrite an application file, and remove the copy afterwards. The injected script posts into the feed, which triggers another browser run, so keep its link harmless. Around a hundred concurrent logins is what the race needs; more will simply stall the instance, and its proxy gives up at sixty seconds.

- status: proposed
