# Field notes — Prototype / class pollution

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

## 2026-09-10 · Secure Notes · proposed

- source note: `solved/secnotes.md`
- chain card: `knowledge/chains/htb-secnotes-mongoose-rename-prototype-pollution-local-gate.json`
- verification: verified_live — HTTP 200 from the gated flag endpoint
- classified as: `web-prototype-pollution` (score 3.5, 3 signals matched)
- also matched: `web-nosqli` (2.5), `web-race-condition` (1.5), `web-ssrf` (1.5)
- signals that fired: $rename, __proto__, prototype pollution

**Confirming probe that worked**

> send an update containing only your own note's filter and no content fields, and read the response

Expected: the matched documents are returned unchanged, proving the filter is attacker-shaped and the call is read-safe

Falsifier: the filter is coerced to a string, so no object reaches the query

**Traps recorded on this solve**

- a broad filter fired before the update semantics are understood mass-updates the collection and can cost the instance
- test update semantics on your own object with the content fields omitted first

**Blast radius**: a broad filter with content fields overwrites every document in the collection and destroys other players' data; always pin the filter to your own object id

- status: proposed

## 2026-09-06 · TornadoService · proposed

- source note: `solved/tornadoservice.md`
- chain card: `knowledge/chains/htb-tornadoservice-bot-csrf-class-pollution.json`
- verification: verified_live — HTTP 200 from /stats with the forged cookie
- classified as: `web-prototype-pollution` (score 3.5, 3 signals matched)
- also matched: `web-auth-session` (3.5), `web-csrf` (3.5), `web-parser-differential` (3.5)
- signals that fired: __class__, class pollution, merge

**Confirming probe that worked**

> fetch a public read endpoint to obtain a valid object id, then confirm the write endpoint answers 403 for a direct request

Expected: 403 that names a local-only restriction, and a readable object id

Falsifier: the write endpoint accepts a direct request, so no bot relay is needed

**Traps recorded on this solve**

- ngrok inserts an interstitial that headless bots cannot pass; a plain SSH reverse tunnel does not
- firing two payload routes at once makes the success unattributable: fire one, wait, then the other

**Blast radius**: the pollution changes a global application setting; other players on a shared instance lose their sessions

- status: proposed

## 2026-09-22 · Sattrack · proposed

- source note: `solved/htb-sattrack-client-side-pp-jsfiles-csp-bypass.md`
- chain card: `knowledge/chains/htb-sattrack-client-side-pp-jsfiles-csp-bypass.json`
- verification: verified_live — The admin bot's own browser exfiltrated its cookie to the collector: {"tag":"hello","cookie":"token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."} decoding to role=admin, email=admin@sattrack.htb. Replaying that cookie returned HTTP 200 from the admin area with the flag in the response body: <div class="font-medium text-white">HTB{...}</div>.
- classified as: `web-prototype-pollution` (score 3.5, 3 signals matched)
- also matched: `web-xss` (3.5), `web-auth-session` (2.5), `web-csrf` (2.5)
- signals that fired: __proto__, merge

**Confirming probe that worked**

> Load the page with the parameter set to JSON containing a __proto__ branch that sets the config key to an array holding a harmless same-origin URL, then read the rendered DOM and check whether a script element with that source was appended.

Expected: A script element carrying the injected source appears in the DOM, proving the prototype write reached the config read and that the polluted value beat the server config fetch.

Falsifier: No such element appears. Either the merge guards __proto__, or the config is read before the merge runs, or the parameter did not survive the page's decode depth. Re-count the decodes before abandoning the class, because the wrong encoding depth looks exactly like a patched merge.

**Traps recorded on this solve**

- Count the decodes, not the encodes. URLSearchParams.get() already percent-decodes; a further decodeURIComponent() is a second decode and a nested URL inside the value needs one extra encoding layer per decode or its '&' and '+' are destroyed. The payload fails silently and the page looks normal.
- A CSP with no img-src inherits default-src, so an offsite new Image().src is dropped. Use fetch() when connect-src is wildcarded. An earlier attempt at this challenge had the whole chain right and still collected nothing for exactly this reason.
- A reflecting endpoint served as text/plain still executes as a script when X-Content-Type-Options: nosniff is absent. Check the header before writing the endpoint off.
- Rehearse the payload in a local headless browser with the origin swapped to the public address before spending a bot cycle; a privileged viewer is rate limited and returns no diagnostics.
- The privileged index page is often a dashboard with no flag. Enumerate its navigation links instead of reading only the index.
- When two ports are supplied, identify them by response content rather than by the order they were given in.
- Keep the application's original script entry inside the polluted array so the page keeps working and the injection stays inconspicuous.

**Blast radius**: Low on the target itself: the pollution lives in the victim's page instance only and nothing server-side is written. The real exposure is outward. The chain needs a publicly reachable collector, so anything the injected script sends leaves the lab and reaches whatever host is used; keep it to the cookie and the flag, and take the collector and any tunnel down as soon as the flag is read. The stolen session belongs to a shared admin account, so do not issue state-changing requests with it.

- status: proposed

## 2026-09-25 · Chromatic Aberration · confirmed

- source note: `CSCV2026/give_to_player/WRITEUP.md`
- chain card: `knowledge/chains/cscv2026-chromatic-mergecatalog-constructor-prototype-ejs-outputfunctionname-rce.json`
- verification: verified_live — Local docker compose harness (edge on 127.0.0.1:18080). POST /api/admin/export-preview with the default chromatic_admin cookie and the constructor.prototype.outputFunctionName exec payload returned HTTP 200 {"html":"CSCV2026{...}\n"}; the same sink with `id` returned uid=10001(renderer) gid=999(renderer), read from the live response. Recorded in challenges/cscv2026-chromatic/state.json via hooks.py pre-flag (source live-response).
- classified as: `web-prototype-pollution` (score 4.5, 4 signals matched)
- also matched: `web-file-upload` (3.5), `web-ssrf` (3.5), `web-command-injection` (3.0)
- signals that fired: Prototype pollution, __proto__, constructor, merge

**Confirming probe that worked**

> POST /api/admin/export-preview with Cookie chromatic_admin=<token> (or the bot) and JSON body {"title":"t","theme":{"constructor":{"prototype":{"outputFunctionName":"x;__append('[PP-MARKER-b4e1]');var y"}}}}

Expected: HTTP 200 and {"html":"[PP-MARKER-b4e1]<!doctype html>..."} - the marker sits before the template, proving the prototype-inherited option reached the ejs compile step without any RCE

Falsifier: 403 administrator session required, or 200 with the marker absent (merge hardened with Object.hasOwn/Object.create(null), or ejs upgraded past 3.1.6)

**Traps recorded on this solve**

- classify.py --source on the challenge directory ranked web-command-injection first because it scanned this repository's own WRITEUP.md; scanning only renderer/ named web-prototype-pollution. Exclude solution notes from a white-box classify input.
- ejs prepends 'var <outputFunctionName> = __append;' - the payload must keep it parseable (end with 'var y') and call process.exit(0) before the engine's own output is written, otherwise the JSON on stdout is either a syntax error or double output
- process.getBuiltinModule needs Node >=20.16/22.3; the fallback is process.mainModule.require('child_process'). Check the runtime before choosing, because a failure here looks identical to the merge not working
- the merge's `!(key in target)` is deliberate: it preserves the inherited constructor, which is exactly what makes constructor.prototype pollution work. A guard that rejects constructor/prototype or uses Object.create(null) kills the chain; confirm the guard from source, do not assume
- the supplied handout's .git/ carried a non-stock core.fsmonitor hook (applypatch-msg.sample) that would git-apply a patch removing the nginx cache-key map and the single __proto__ check. It did not fire because there was no index, and by the time of this run .git/config had no core.fsmonitor and the hook was a 17-byte stub; the bugs were still present in the source
- the full bot path (cache-key collision -> archive block -> board-compat.js -> admin export-preview) is NOT verified end to end here: the unresolved link is which GET /api/...?workspace=<W> can return an attacker body that JSON.parses as the manifest, since /api/media/raw must sniff as an image and must not start with { or [, and /api/telemetry/:channel is res.json()-wrapped

**Blast radius**: Local harness: one renderer worker is spawned per job with a 2.5s timeout and the Object.prototype write dies with that process, so there is nothing to clean up. On a shared instance the same request is RCE as uid renderer and can read the flag; it does not write to disk. The second-order path would leave a poisoned nginx cache entry for up to 10 minutes and may write one uploaded asset.

- status: confirmed
