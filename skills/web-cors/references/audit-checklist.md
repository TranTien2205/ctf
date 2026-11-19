# Audit checklist — the CORS sweep, every item

A printable run — the full verification of a CORS surface.

## The endpoint inventory
- [ ] the session-data endpoints identified — /api/me, /api/flag, /api/token
- [ ] the flag-carrying endpoint confirmed — the response contains the flag
- [ ] the endpoint's content-type noted — JSON vs HTML (read method)
- [ ] the endpoint's auth noted — cookie vs Bearer

## The ACAO measurement
- [ ] the foreign-Origin replay run — `curl -H 'Origin: evil.com'`
- [ ] the ACAO value recorded — reflected/*/`null`/fixed/absent
- [ ] a fixed ACAO's allowlist tested — is your origin in it
- [ ] the `Vary: Origin` noted — per-origin or shared-cache

## The check-shape battery
- [ ] reflect — `https://evil.com`
- [ ] null — `null`
- [ ] prefix — `https://target.com.evil.com`
- [ ] suffix — `https://eviltarget.com`
- [ ] substring — `https://evil-target.com`
- [ ] subdomain — `https://sub.target.com`
- [ ] userinfo — `https://target.com@evil.com`
- [ ] query — `https://evil.com?target.com`
- [ ] encoded-dot — `https://target.com%2eevil.com`
- [ ] special-char — `https://target`com`
- [ ] scheme — `http://target.com`
- [ ] trailing-dot — `https://target.com.`

## The credential gate
- [ ] ACAC measured — true/absent
- [ ] the cookie's SameSite noted — None/Lax/Strict
- [ ] a non-cookie credential checked — a Bearer/API-key
- [ ] the `*+ACAC` combo ruled out — invalid

## The preflight
- [ ] the OPTIONS preflight tested — the method+header ask
- [ ] the ACAM checked — the method allowed
- [ ] the ACAH checked — the header allowed
- [ ] the simple-request bypass noted — no-preflight path

## The exploit page
- [ ] the fetch is `credentials:'include'`
- [ ] the read method matches the content-type — `.json()`/`.text()`
- [ ] the exfil channel chosen — fetch/img/beacon/ws/writeback
- [ ] the page's origin matches the CORS allowlist

## The delivery
- [ ] the bot endpoint found — /report, /visit, admin-trigger
- [ ] the bot's session confirmed — a flag cookie, logged-in context
- [ ] the bot's reachability noted — external / airgapped / data:
- [ ] the exfil's reachability confirmed — can the bot reach the listener

## The readback
- [ ] the OOB listener up — `oob_listener serve`
- [ ] the exfil hit verified — the data in the hit log
- [ ] the data attributed — a unique session field proves the bot's read
- [ ] the flag extracted — the `FLAG{...}` in the exfil

## The evidence
- [ ] the hypothesis recorded — `state.py --hypothesis`
- [ ] the verdict recorded — `hooks.py post-probe --verdict`
- [ ] the flag gated — `hooks.py pre-flag`
- [ ] the negative results recorded — every gate that held

## The falsifier
- [ ] a `*` on the sensitive endpoint ruled out — public read
- [ ] a non-credentialed read ruled out — ACAC absent or cookie-gated
- [ ] a strict allowlist + no bypass → dead → pivot recorded

## The boundary check
- [ ] not a CSRF-write (a `no-cors` write doesn't need CORS)
- [ ] not an XSS (a same-origin read subsumes CORS)
- [ ] not an XS-leak (a side-channel, not a data read)
- [ ] not a JSONP (a script-tag read, no CORS)
- [ ] not a websocket (a ws channel, not a fetch)
