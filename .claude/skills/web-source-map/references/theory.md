# Theory — why the front-end gives the game away

## The shipped-source principle

A single-page app must ship its logic to the client — there is no
server-side render to hide behind. Everything the front-end does is in
the bundle: every endpoint it calls, every route it knows, every config
value it reads. The attacker does not guess the surface; the app
*declares* it.

## The minification fiction

Minification removes readability, not information. Identifiers are
renamed but string literals survive — URLs, paths, param names, flags,
secrets are what the runtime needs, so they remain. A minified bundle
is a compressed spec, not a hidden one. Obfuscation raises the cost of
reading but cannot remove the strings the program needs.

## The source-map leak

A `.map` is a debugging artifact the build produces and the deployment
sometimes ships. It maps minified positions to original source — and
`sourcesContent` inlines the *entire original file*. A shipped map
turns "compressed spec" into "the actual commented source". It is the
single highest-value recon artifact a front-end can leak.

## The trust boundary inversion

The front-end is attacker-controlled *and* attacker-readable. Every
"hidden" admin route, every "private" key, every "internal" endpoint in
the bundle is already public — the server shipped it. The only thing
protecting a client-side secret is obscurity, which is not protection.

## The recon-vs-guess asymmetry

Directory brute force guesses paths from a wordlist; bundle mining
*enumerates* the real paths from the client's own code. The map is
strictly more complete than a guess — it is the route table the app
itself uses. A challenge that ships a SPA has already told you its
surface; the work is reading it.

## The layered recon order

The map sits in a broader recon: entry page → scripts → bundle → map →
`.git`/`.env`/backups. Each layer names more of the surface. The map
is often the richest single layer because it carries the *original
source*, not just paths.
