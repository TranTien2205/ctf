# Field notes — Cross-site scripting

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

## 2026-09-18 · xss (Full Stack Conf) · proposed

- source note: `solved/htb-fullstackconf-stored-xss-innerhtml-socketio-flag.md`
- chain card: `knowledge/chains/htb-fullstackconf-blind-stored-xss-socketio-oracle.json`
- verification: verified_live — the flag arrived inside an event frame pushed by the live target on its own push channel, in response to a stored payload executing in the renderer
- classified as: `web-xss` (score 2.5, 2 signals matched)
- also matched: `web-race-condition` (1.5), `web-ssrf` (1.5), `web-sqli` (1.5)
- signals that fired: innerHTML, xss

**Confirming probe that worked**

> open the push channel, leave it idle briefly to confirm it stays silent, then submit an image element with an error handler as the stored value and keep the channel open for about two minutes

Expected: a frame arrives on the channel carrying the reward payload

Falsifier: the channel delivers unrelated traffic while idle, so silence proves nothing, or repeated submissions across contexts produce no frame at all

**Traps recorded on this solve**

- an element whose handler fires while a plain script element does not is the signature of insertion through an HTML property rather than a parser, so carry the handler-based payload first and do not read a failing script element as the value being escaped
- one silent run is not a negative on a bot-driven target: the first attempt with a payload that was later proven to work saw nothing for ninety seconds, and the difference was never explained, so re-run before discarding a payload
- confirm the channel is one that stays open until the server has data before treating its silence as a result
- a comment declaring the push channel is not part of the challenge is misleading; it is not part of the bug but it is the entire exfiltration path

**Blast radius**: the submission is an ordinary newsletter registration and each payload stores one row that a shared renderer will execute. Keep the payload to a harmless dialog, never a redirect, a request to an outside host, or anything that changes state, because other players' sessions are rendered by the same component. Do not repeat the batch once it has fired.

- status: proposed

## 2026-09-23 · QuickBlog · proposed

- source note: `solved/htb-quickblog-codefence-xss-registration-oracle-pickle-session.md`
- chain card: `knowledge/chains/htb-quickblog-codefence-xss-registration-oracle-pickle-session.json`
- verification: verified_live — GET /admin with the recovered cookie returned 200 containing 'admin page, admin_user.', and after the session-store write GET /uploads/res.txt returned the flag in the response body. After the cleanup run the same path returns 404 and re-sending both planted cookies produces nothing.
- classified as: `web-xss` (score 4.5, 4 signals matched)
- also matched: `web-ssrf` (3.5), `web-file-upload` (2.5), `web-ssti` (2.5)
- signals that fired: XSS, admin bot, innerHTML, unescape

**Confirming probe that worked**

> Store a code fence whose language field closes the attribute and adds autofocus with a tabindex and an onfocus that is a percent-encoded eval(unescape(...)), then load the page yourself in a real browser.

Expected: The handler fires on insertion with no interaction, proving both that the attribute sink is reachable through the incomplete escaping and that the case-folding filter does not stop a reconstituted payload.

Falsifier: The attribute is escaped, or the handler never fires without interaction, meaning the sink is not injectable and the privileged browser cannot be made to run anything.

**Traps recorded on this solve**

- A bot that logs in again on every run has a different session id each time, so a shared exfiltration namespace mixes runs into a value that is not any real id. Lock the namespace to one run.
- The registration oracle WRITES: probing a name creates it, so probing before the privileged visit hands the bot a name it can no longer create and that symbol is lost. Never probe the lock name at all.
- Registration overwrites the session's own username, so the exfiltration requests have to omit credentials or the stolen session is demoted before it can be used.
- A template literal cannot be an object key; `{`Content-Type`: ...}` is a SyntaxError. Percent-encoding already makes ordinary double quotes safe inside the attribute.
- The framework's session loader expects a (data, expiration) tuple. Pickling the bare payload still executes but then raises, which is noisier than pickling the expected shape.
- A single-threaded http.server deadlocks headless Chrome, which opens several connections; local rehearsals need ThreadingHTTPServer.
- The flag name is randomised at container start, so it has to be globbed, and a setuid helper is usually the intended reader.

**Blast radius**: The pickled session file executes as the application user for anyone who sets that cookie, so it is a remote backdoor until removed; make the payload delete it in the same command. The exfiltration registers several hundred throwaway accounts and the stored payload keeps firing on every scheduled visit, both of which live in process memory and only clear on restart. Do not point the injected command at configuration or at imported modules. On a shared instance the registration oracle is several hundred sequential writes: keep concurrency low and never probe a namespace the payload has not written yet, because probing creates the name and destroys that symbol.

- status: proposed
