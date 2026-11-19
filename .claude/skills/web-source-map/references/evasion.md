# Evasion — when the bundle fights back

## Note: recon, not payload evasion

`web-source-map` is a read of shipped files — there is no WAF to evade
in the fetch itself. The "evasion" here is the *bundle's* resistance to
being read, and the adjacent info-disclosure probes a lax deployment
permits.

## The obfuscation wall

String-array obfuscation, control-flow flattening, encoded literals —
the bundle resists reading but cannot remove the strings the runtime
needs. Responses:

- `strings` the bundle, grep for the *shape* (`/api/`, `token`, `flag{`)
- extract the packed string array at the bundle head and decode lookups
- `js-beautify`/`prettier` to reformat, then read the structure
- a deobfuscator as a last resort; endpoints usually survive as strings

## The map-disabled build

Production disables sourcemaps — the common case, not a blocker.
Fallback: string mining on the bundle yields endpoints/params/flags
even without a map. The map is a bonus, not a requirement.

## The minified-not-obfuscated case

A minified-but-not-obfuscated bundle reads as dense but readable code —
`js-beautify` reformats it into near-source. Beautify-then-read is the
middle path between grep and a full map.

## The adjacent disclosure

A deployment lax enough to ship `.map` often ships more — the probe
order after the map:

```
.map -> /.git/HEAD -> /.env -> /backup.zip -> /src/ -> /static/maps/ ->
asset-manifest.json -> _buildManifest.js -> __NEXT_DATA__ -> sw.js
```

Each is a different file the server may serve publicly. The map's
presence is a signal to probe the rest.

## The authenticated bundle

A session-gated app serves the bundle only to logged-in users —
`bundle_miner -H "Cookie: session=..."` passes the session. The bundle
is then the *authenticated* surface: routes and endpoints a guest
cannot see.

## The per-environment bundle

A `?env=dev`, `.dev` host, or `main.dev.js` may ship a richer bundle —
sourcemaps on, debug flags set, dev endpoints present. A dev build is
a higher-yield target than the prod bundle.
