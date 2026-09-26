# Field notes — Cache poisoning / deception

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

## 2026-09-21 · EncoDecept · confirmed

- source note: `solved/encodecept.md`
- chain card: `knowledge/chains/htb-encodecept-charset-xss-cache-deception-orm-oracle-marshal-rce.json`
- verification: verified_live — the flag was written to the Rails public directory by the Marshal RCE and read back over HTTP 200 on the live target
- classified as: `web-cache-poisoning` (score 2.0, 2 signals matched)
- also matched: `web-race-condition` (2.5), `web-prototype-pollution` (2.5), `web-ssrf` (2.5)
- signals that fired: cache, x-cache

**Confirming probe that worked**

> authenticated GET /settings.html?cb=1 twice, then anonymous GET /settings.html?cb=1

Expected: the anonymous request returns 200 with X-Cache-Status HIT and the body of the authenticated page

Falsifier: the anonymous request is a 302 to /login, so the proxy does not serve an authenticated page anonymously

**Traps recorded on this solve**

- report the internal 127.0.0.1 URL to the bot, not the public address, or the bot session is not used
- .ico is rendered as an image by Chrome, so the cached HTML never executes; use .html
- the Marshal gadget needs the detection step first or it raises Errno::ENOENT on the git cache directory
- the gadget is tied to the exact Ruby and gem build and can fail on a patched image
- the flag file written into the web root may not be removable afterwards; reset the instance

**Blast radius**: cache poisoning affects every player who requests the cached URL until it expires; the XSS and RCE act as the privileged bot and can write files inside the container, so use a disposable cachebuster and remove created templates

- status: confirmed

## 2026-09-23 · OmniWatch · proposed

- source note: `solved/htb-omniwatch-varnish-urlless-cachekey-zig-crlf-poison-jwt-forge.md`
- chain card: `knowledge/chains/htb-omniwatch-varnish-urlless-cachekey-zig-crlf-poison-jwt-forge.json`
- verification: verified_live — GET /controller/home returned the injected body with X-Cache: HIT; the bot's session cookie arrived through a second slot; the firmware endpoint returned the JWT secret; the stacked-query injection answered 200 and GET /controller/admin with the forged token returned the flag. After the cleanup injection the same token redirects to /controller/login and /controller/home answers its real 302 again.
- classified as: `web-cache-poisoning` (score 4.5, 4 signals matched)
- also matched: `web-race-condition` (3.5), `web-auth-session` (3.5), `web-request-smuggling` (2.5)
- signals that fired: Cache-Control, X-Cache, cache, varnish

**Confirming probe that worked**

> Request an oracle URL whose path segment injects the cache's storability header through %0d%0a, then request a completely different path on the other backend with the same CacheKey header.

Expected: The second request answers X-Cache: HIT with the first response's body, proving the cache key excludes the URL and that the injected header made the response storable.

Falsifier: The second request is a MISS, or the injected header never appears, meaning the hash includes the URL or the header value is validated.

**Traps recorded on this solve**

- Reading an empty cache slot is destructive: a backend response with ttl <= 0 is turned into an uncacheable hit-for-miss object with a 120s lifetime by the builtin VCL, which swallows every later write to that slot.
- A same-origin fetch sends cookies by default, and the builtin VCL passes any request carrying a Cookie, so the response is never stored. Use credentials omitted for anything meant to land in the cache.
- A poison request that HITs does not overwrite the object and does not extend its TTL, so a stale process from an earlier attempt pins the slot and silently serves an old payload.
- Two writes into the same slot within one object lifetime collapse into one; the first wins and the second is lost with a 200 response.
- Slot names derived from the clock need the skew measured from the response Date header.
- A literal slash inside an injected header value adds a path segment and breaks routing, which surfaces as a 404 and not as a failed injection.
- An injected byte that does not form a complete header line makes the cache reject the backend response with a 502 or 503 - which is positive evidence the injection reached the header block.
- SubtleCrypto is undefined outside a secure context, so in-browser crypto works on a loopback origin and nowhere else; it cannot be rehearsed.
- Poisoning the slot before the automation has passed its login page replaces the form it drives and the run aborts, so the poisoned page must carry a working copy of that form.

**Blast radius**: A poisoned slot is served to every visitor, including the privileged bot, for the object's lifetime, and replacing a login page stops the bot working entirely. The forged role is created by writing a row into the table the authentication middleware trusts, so it survives until deleted and is usable by anyone holding the token. The stacked-query primitive runs with whatever grants the application user has; on this target that included DELETE on the signature table. Polling cache slots is itself destructive: an empty slot that is read becomes uncacheable for two minutes.

- status: proposed

## 2026-09-23 · Pod Diagnostics · proposed

- source note: `solved/pod_diagnostics.md`
- chain card: `knowledge/chains/htb-pod-diagnostics-arg-cache-key-duplicate-param-poisoning-renderer-file-read.json`
- verification: verified_live — the flag was reassembled from four chunks read back out of the cache channel and decoded locally, and tools/hooks.py pre-flag accepted it as a live response
- classified as: `web-cache-poisoning` (score 1.5, 1 signals matched)
- also matched: `web-prototype-pollution` (5.5), `web-ssti` (3.5), `web-ssrf` (3.5)
- signals that fired: cache

**Confirming probe that worked**

> after the cache validity has elapsed, request the cached route with the keyed argument given twice, then request it again with only the first value

Expected: the second request returns the value that was supplied as the duplicate, proving the entry was keyed on the first value alone

Falsifier: the second request returns the ordinary response, so either the key covers more than that argument or the poisoning request was itself served from cache

**Traps recorded on this solve**

- a poisoning request arriving while the entry is still valid is served from cache and poisons nothing; compare a timestamp in the body to tell a hit from a miss
- the window cannot be widened, so the trigger has to follow the poisoning immediately
- an assignment to innerHTML does not execute a script element
- the renderer's navigation timeout is short and a nested render consumes nearly all of it
- reading an exfiltration key before it is written blocks the write for a whole validity window
- a browser-rendered document holds glyph identifiers rather than text, so a plain search for the flag finds nothing even when the bytes are correct
- a setuid helper in the image can be a decoy when the supervisor gives no user directive and the renderer is already root

**Blast radius**: nothing persistent is written: no files, no database rows, no accounts. The only state touched is the proxy cache, and every entry expires within its validity window, so the target returns to normal on its own within seconds. The one real hazard is self-inflicted - reading an exfiltration key too early blocks the payload's write for a full window - and the renderer is triggered once per attempt, so keep attempts few because each one launches a browser.

- status: proposed

## 2026-09-25 · Chromatic Aberration · confirmed

- source note: `CSCV2026/give_to_player/solve_chromatic.py`
- chain card: `knowledge/chains/cscv2026-chromatic-xssi-json-svg-polyglot-cache-key-collision-bot-rce.json`
- verification: verified_live — Local docker compose harness (edge 127.0.0.1:18080): solve_chromatic.py ran all 4 stages - upload 201 image/svg+xml (asset fde9d231...), poisoned manifest cache verified, /api/report accepted, then GET /api/telemetry/<channel> returned {"html":"CSCV2026{...}\n"} and reported FLAG. Recorded through tools/hooks.py; the polyglot is the previously-unresolved raw-body gadget.
- classified as: `web-cache-poisoning` (score 2.5, 2 signals matched)
- also matched: `web-prototype-pollution` (4.5), `web-file-upload` (3.5), `web-ssrf` (3.5)
- signals that fired: age:, cache

**Confirming probe that worked**

> upload the XSSI/JSON/SVG polyglot (body starts " )]}',\n " and contains '"svg":"<!DOCTYPE svg><svg xmlns=\"http://www.w3.org/2000/svg\"></svg>"'), then GET /api/media/raw?id=<asset>&workspace=<W> followed by GET /api/workspaces/manifest?workspace=<W>

Expected: upload -> 201 {"mime":"image/svg+xml"}; the manifest request returns the uploaded body (starts with )]}',) instead of the fixed 'Untitled workspace' JSON

Falsifier: upload -> 415 unsupported image or invalid image signature; or the manifest request returns the normal fixed manifest, meaning the cache key includes the full request_uri

**Traps recorded on this solve**

- plain '<svg' or '<?xml' inside a JSON string is NOT enough: file(1) still says application/json/text. The token that flips libmagic to image/svg+xml is '<!DOCTYPE svg>' inside the JSON string value while the file begins with the XSSI prefix
- the XSSI prefix must match Angular's PI regex /^\)\]\}',?\n/ exactly, i.e. )]}',\n ; a missing newline or comma placement makes Angular's strip fail and JSON.parse throws
- hasDocumentPreamble only inspects the first 64 bytes and only rejects a first non-space of { or [; the XSSI prefix passes it, but a plain JSON object starting with { is rejected - do not drop the prefix
- scripts inserted through [innerHTML]/bypassSecurityTrustHtml do not execute; the markup must load board-compat.js from a same-origin <iframe srcdoc> so CSP script-src 'self' allows it
- the archive packet is only accepted when integrity == FNV-1a32(markup) as 8 lowercase hex; recompute it over the exact markup bytes
- if the deployed ADMIN_TOKEN was rotated, the fast path (POST /api/admin/export-preview with the token) returns 403 and this bot chain is the only route
- the XML mime detection depends on the host's libmagic build; verify `file --brief --mime-type <polyglot>` == image/svg+xml before uploading

**Blast radius**: Local harness: one uploaded asset, one poisoned nginx cache entry for workspace <W> (10m, unique per run) and one short-lived telemetry channel. On a shared instance the same chain is RCE as uid renderer and reads /flag via /readflag; it writes no files. Use a fresh random workspace/channel per attempt and never reuse the victim's.

- status: confirmed