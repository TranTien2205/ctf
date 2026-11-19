# Per-falsifier — the kill map, cell by cell

## Cell 1: no exposed endpoint

- **Probe**: `POST /session` on `:9515`,`:4444`,`/wd/hub/session`,`/session`.
- **Kill state**: all refused/404.
- **Re-open**: another port/route answers; a Grid found.
- **Closes**: the entire attack-surface use.

## Cell 2: file read dead

- **Probe**: navigate `file:///etc/passwd` -> `source`.
- **Kill state**: error page, blocked scheme, empty source.
- **Re-open**: `execute` `fetch("file://")` works; a different scheme.
- **Closes**: the file-read primitive (both nav and JS forms).

## Cell 3: JS execution dead

- **Probe**: `execute/sync` `return 1+1`.
- **Kill state**: permissions/disabled error.
- **Re-open**: `execute/async` allowed; CDP `Runtime.evaluate` exposed.
- **Closes**: the JS-in-browser primitive (cookie/storage/fetch reads).

## Cell 4: loopback reach dead

- **Probe**: navigate `localhost` admin/debug/internal routes.
- **Kill state**: same-as-external, refused, or nothing extra.
- **Re-open**: a different internal port/service answers.
- **Closes**: the loopback-origin surface.

## Cell 5: reproduction impossible

- **Probe**: build the local bot from bot-source or observation.
- **Kill state**: no source AND no observable properties to copy.
- **Re-open**: the bot's source is found / more of it is observed.
- **Closes**: faithful local development (not the class — you can
  still develop blind, just less efficiently).

## Cell 6: channel unreachable

- **Probe**: `fetch`/`goto` your own tunnel from inside the driver.
- **Kill state**: interstitial, refused, filtered.
- **Re-open**: a different tunnel; a same-origin channel; DNS.
- **Closes**: that exfil channel for headless.

## Cell 7: flag not in browser-reachable surface

- **Probe**: sweep the surfaces — file, cookie, storage, DOM, localhost.
- **Kill state**: the flag is nowhere the browser reaches.
- **Re-open**: a new surface (a route, a store) is found.
- **Closes**: the attack-surface use for *this* flag path.

## Cell 8: bot flow does not exist

- **Probe**: is there a report/admin-visit flow at all?
- **Kill state**: no bot visits, no bot source, the "bot" is a server fetch.
- **Re-open**: a real bot flow is found; the "bot" is actually SSRF.
- **Closes**: the debugging-aid use — and possibly the whole class.

## The compound falsifier

The class dies when cells 1+5 (attack surface AND reproduction) are
both dead — no endpoint to attack and no bot worth reproducing. Until
both are dead, the class has a live use.

## The budget falsifier

Five genuine mechanism-layer iterations (context, channel, timing,
reproduction, surface) with no new signal -> `tools/decide.py` answers
`escalate`. A spent layer is a measured state, not "keep trying".
