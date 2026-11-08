# Field notes — web-xs-leaks

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

## 2026-09-27 · Stylish · confirmed

- source note: `challenges/Stylish/challenge/helpers/TokenHelper.js`
- chain card: `knowledge/chains/htb-stylish-css-unicode-range-token-leak-bot-selforigin-approve-sqlite-limit-blind.json`
- verification: verified_live — Live HTB instance. The unicode-range stylesheet produced exactly 32 font requests out of 62 offered, whose sorted characters gave the token; a second stylesheet pointing a font at the same-origin approve route flipped /view/4 from 403 to 200; the LIMIT oracle then yielded the table name flag_dd38f088 and the flag. Recorded in challenges/stylish/state.json through tools/hooks.py post-probe (confirms, evidence-kind class then impact) and pre-flag (source live-response). Tunnel and listener were torn down afterwards and verified refusing.
- classified as: `web-xs-leaks` (score 0.54, 1 signals matched)
- also matched: `web-logic-flaw` (1.51), `web-sqli` (0.98), `web-ssrf` (0.94)
- signals that fired: puppeteer

**Confirming probe that worked**

> submit a stylesheet containing a single @font-face with an absolute URL on a host you control and font-family applied to body, then wait for the bot

Expected: one request arrives at your listener: the bot loads attacker CSS and font-src really does permit an external host

Falsifier: nothing arrives. Before blaming the challenge, check the two failure modes in the traps: a tunnel that intercepts browser user agents, and a stylesheet URL that 404s because the file is written asynchronously after the bot is dispatched

**Traps recorded on this solve**

- ngrok's free tier is unusable as the listener here. Its browser interstitial fires on the bot's Chrome user agent, answers 200 with its own HTML, and the request never reaches your server; a curl test passes and hides the problem. Measured: same URL, curl reaches the listener, browser user agent does not. ngrok TCP endpoints would avoid it but are card-gated on a free account (ERR_NGROK_8013). An ssh reverse tunnel (localhost.run) passed browser user agents straight through.
- guard against JavaScript truthiness in the oracle: the route checks `if (submissionID && pagination)` and a numeric 0 is falsy, so it falls through and sends NO response at all. That reads as a client timeout rather than an answer. Send pagination as a STRING so "0" stays truthy and still means LIMIT 0.
- the stylesheet is written with an asynchronous fs.writeFile and the bot is dispatched on the same tick, so the first visit can race the file into existence. Confirm the file is actually served at /card_styles/<id>.css before concluding the CSS is not being applied.
- the secret's element is hidden by a utility class that uses !important, so display:block alone does nothing and no character is ever rendered. The override needs !important too, and if the element is not rendered no font is ever requested, which looks exactly like the leak failing.
- only the element you style leaks. The page carries a second token in an identically hidden element; leaving it hidden keeps its characters out of the result, which is what makes the 32 hits unambiguous rather than a union of two tokens.
- the flag table name is randomised per boot, so read sqlite_master first; PRAGMA case_sensitive_like=ON is set, so a LIKE pattern has to match the real case.
- a stale module-shadowing file in the working directory will break the extractor before it sends a single request (a local inspect.py shadowed the standard library here). Keep exploit scripts out of directories holding files named after standard modules.

**Blast radius**: Read-only against the target apart from rows it is designed to accept: a few submissions, one comment, and one submission flipped to approved. None of those can be removed without the reject token, so keep the count low. The real exposure is on YOUR side: this chain needs a public listener, so a tunnel is opened to the internet for the duration. Bind the listener to loopback, keep the tunnel up only for the leak, and tear it down and verify it is refusing connections afterwards. Nothing but font paths ever reaches it.

- status: confirmed
