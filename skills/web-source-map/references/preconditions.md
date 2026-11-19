# Preconditions — what must be true to run this route

## The surface precondition

The app ships a JavaScript bundle — a SPA (React, Vue, Next, Angular)
or a webpack/Vite/Rollup/esbuild build. A server-rendered page with no
app code is not this route.

## The reachability precondition

The bundle (and `.map` if present) is fetchable — `curl` returns it.
A session-gated app needs the session (`bundle_miner -H "Cookie: ..."`).

## The value precondition

There is something to find — the front-end names endpoints, secrets,
flags, or routes the rendered page hides. If the bundle is a thin
loader for a server-rendered app, the surface is thin.

## The honesty precondition

Leads from the bundle are verified live before being claimed — the
bundle is attacker-controlled data, not ground truth.

## The tool precondition

`bundle_miner` is stdlib + `bs4`/`lxml` (auto-fallback to regex); no
external deps needed. `--selftest` proves it offline.

## The "not this route" checks

- no `.js` bundle → not this route
- a `.map` `200 text/html` is a catch-all, not a map
- a minified bundle with no map yields strings, not source
- the map is recon — the exploit is the routed class
