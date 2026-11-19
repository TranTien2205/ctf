# Mechanism — what a bundle and a source map are

## The two artifacts

`web-source-map` covers two related front-end artifacts, and the skill
only makes sense once they are separated.

**The bundle** — the JavaScript the app ships: a single `main.js`, a
set of chunks, `/_next/static/`, `/static/js/`, `/assets/index-*.js`.
It is *minified* — the original source is collapsed into unreadable
code, but the strings inside it still carry endpoints, route paths,
parameter names, feature flags, and sometimes secrets.

**The source map** — a `*.js.map` file referenced by a `//#
sourceMappingURL=` comment. It maps the minified positions back to the
original source — filenames, line numbers, and (when
`sourcesContent` is present) the *full original source code*. A source
map is the front-end's real source; a bundle without one is only
strings.

## Why it matters

The front-end is source too — a single-page app ships its entire
client-side logic to every visitor. Inside the bundle and map are:

- **endpoints** — every `fetch`/`axios`/`api/` URL the client calls
- **route paths** — every page/route the SPA knows, including hidden
  and admin ones
- **parameter names** — the keys the client sends, which name the
  server's expectations
- **feature flags** — `feature.X`, `config.debug`, `flags.*` — gates
  the front-end hides but the server may not
- **secrets** — API keys, tokens, JWTs, signing keys left in source
- **the real logic** — when `sourcesContent` is present, the original
  commented source, not minified code

## The two mining paths

**String mining** (no map) — extract the readable strings from the
minified bundle: URLs, paths, param names, key-like tokens. Fast, but
only surfaces what survives as literal strings.

**Source reconstruction** (map present) — decode the `.map`, recover
`sources` + `sourcesContent`, write the original files back to disk.
Yields the real source — comments, logic, structure — not just
strings.

`tools/web/bundle_miner.py` does both: `--url`/`--file`/`--map` for
input, `--out` for source reconstruction, and it inventories endpoints
and secret candidates automatically.

## The honesty rule

A bundle's strings are *attacker-controlled data* — a `sources` path
inside a `.map` can be a traversal (`../../../etc/passwd`), which is
why `bundle_miner` rejects a `sources` path that escapes `--out` and
counts it. Treat recovered sources as untrusted: read them, do not
execute them, and verify any "secret" is real before acting on it.

## What it is NOT

- **not directory brute force** — the bundle *names* real endpoints;
  brute-forcing paths is `../web-triage/`'s job after the map gives
  the real list.
- **not a vulnerability class** — it is *recon*: it feeds every other
  class (IDOR, auth, logic, info-disclosure) the endpoints and secrets
  they need.
- **not the app's backend source** — the map is the *front-end* source;
  the server logic is only what the client shipped.
