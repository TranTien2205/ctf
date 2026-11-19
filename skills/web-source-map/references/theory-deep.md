# Theory (deep) — the information-theoretic case for bundle mining

## The shipped-source theorem

A client-side application *must* ship its logic to execute it — there is
no server-side render to hide behind. The bundle is a lossless
compression of the app's client-side behavior: every endpoint it calls,
every route it knows, every config value it reads, every gate it checks.
The attacker does not guess the surface; the application *declares* it.

## Why minification does not hide

Minification optimizes for size, not secrecy. It removes whitespace and
renames *identifiers* — but it cannot remove the *string literals* the
runtime needs: URLs, paths, param names, flag values, config keys. Those
are the program's data, not its names. A minified bundle is a
*compressed spec*, not a hidden one. The identifiers are mangled; the
endpoints, keys, and routes are not.

## Why obfuscation only raises cost

Obfuscation (string arrays, control-flow flattening, encoding) hides the
*logic* — the control flow and the identifier semantics. It cannot hide
the *literals* — a string-array obfuscator moves the strings into an
array, but the array is still in the bundle. The literals survive as
data; grep for the *shape* recovers them. Deobfuscation is a means, not
a requirement — the endpoints are there whether or not the code reads
cleanly.

## The source-map disclosure

A `.map` is a debugging artifact the build produces — and sometimes the
deployment ships it. `sourcesContent` inlines the *entire original
source* — not the mangled spec but the commented, structured, named
code. The map is the difference between "the client's compressed
behavior" and "the developer's actual source".

## The trust-boundary inversion

The front-end is simultaneously attacker-*controlled* (the client runs
it) and attacker-*readable* (the client ships it). Every "hidden" admin
route, "private" key, "internal" endpoint, "gated" feature in the bundle
is already public — the server shipped it to every visitor. The only
protection a client-side secret has is obscurity, which is not
protection.

## The recon-vs-guess asymmetry

Directory brute force enumerates paths from a wordlist — a *sample* of
possible paths. Bundle mining enumerates paths from the client's *own
code* — the *complete* set of real paths the app calls. The map is
strictly more complete than a guess: it is the route table the app
itself uses. A challenge that ships a SPA has already declared its
surface; the work is reading it.

## The lead-economics principle

The map's value is not the endpoint count — it is the *one hidden
endpoint* the UI never shows. A single hidden `/api/admin` or a live
key justifies the whole recon pass. The map is a lead generator; the
downstream class turns one lead into the finding.
