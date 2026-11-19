# Preconditions (deep) — what must hold for this route

## The surface precondition

The app ships a JavaScript bundle — a SPA (React, Vue, Next, Angular)
or a webpack/Vite/Rollup/esbuild build. **Falsifier**: the entry page
loads no application `.js` — a server-rendered app with only CDN libs.
No shipped client logic → not this route.

## The reachability precondition

The bundle (and `.map` if present) is fetchable. A session-gated app
needs the session (`bundle_miner -H "Cookie: $C"`); a dev bundle needs
a dev host. **Falsifier**: the bundle 401/403s and no session is
available → limited to the public surface.

## The value precondition

There is something to find — the front-end names endpoints, secrets,
flags, or routes the rendered page hides. A thin loader for a
server-rendered app has a thin surface. **Falsifier**: the bundle is a
pure loader with no app code → the surface is server-side, not this
route.

## The honesty precondition

Leads are verified live before being claimed — the bundle is
attacker-controlled data, not ground truth. **Falsifier**: a lead that
cannot be verified live stays a lead, not a finding.

## The tool precondition

`bundle_miner` is stdlib + `bs4`/`lxml` (auto-fallback to regex); no
external deps. `python3 tools/web/bundle_miner.py --selftest` proves it
offline. `js-beautify`/`prettier`/`webcrack` are optional deobfuscation
aids, not required.

## The "not this route" checks

- no `.js` application bundle → not this route
- a `.map` `200 text/html` is a catch-all, not a map
- a minified bundle with no map yields strings, not source — do not
  claim the source
- the map is recon — the exploit is the routed class, not this layer
- a WASM-backing app — the logic is in `.wasm`, a different recon

## The environment note

The measured tree has `requests`, `bs4`, `lxml`, `selenium`,
`playwright` — a JS-rendered page that hides its scripts from a plain
`curl` can be driven with the browser (`web-chromedriver`) to capture
the real bundle set.
