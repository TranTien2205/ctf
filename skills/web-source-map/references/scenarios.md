# Scenarios — the target shapes and the pass for each

## Scenario: a Next.js app with a `_buildManifest`

```
entry -> __NEXT_DATA__ + buildId -> _buildManifest.js -> every route +
chunk -> fetch each page chunk -> mine it -> the hidden /admin endpoint
-> verify -> web-idor
```

The manifest is the route map; the page chunks are the spec.

## Scenario: a CRA app with a `.map`

```
entry -> /static/js/main.[h].js -> .js.map 200 json -> bundle_miner
--map --out -> recovered src/ -> grep for flag{, secret, sink ->
pre-flag / route to sink's class
```

The map is the recovery; the source is the find.

## Scenario: a Vue app, no map

```
entry -> /js/app.[h].js + chunk-vendors + route chunks -> no .map ->
string mine every chunk -> /api/internal + apiKey -> verify key live ->
web-auth-session; verify endpoint live -> web-idor
```

No map → string mining; the leads still verify.

## Scenario: an Angular app with a lazy admin module

```
entry -> main.[h].js names loadChildren for /admin -> the lazy chunk
[n].[h].js is public -> fetch + mine it -> /api/admin/export ->
curl it -> public -> web-logic-flaw
```

The lazy chunk is public; the load was client-gated.

## Scenario: an obfuscated bundle

```
entry -> bundle obfuscated (string array) -> strings + shape-grep ->
/api/, token, flag{ survive -> verify each lead -> route
```

Obfuscation hides logic, not literals — grep for the shape.

## Scenario: a session-gated app

```
login -> get the session -> bundle_miner -H"Cookie: $C" -> the
authenticated bundle's richer route table -> the admin endpoints a
guest cannot see
```

The authenticated bundle is the richer surface.

## Scenario: a `.map` presence → adjacent disclosure

```
.js.map 200s -> lax-deployment signal -> /.git/HEAD -> git-dump the
tree -> the server source -> the bigger leak
```

The map is the signal; `.git` is the bigger door.

## Scenario: a Vite dev-served app

```
entry -> /@vite/, /@fs/, /src/ paths -> dev server -> the real source
at /src/ -> read it directly
```

A dev server serves the real source — no map needed.

## Scenario: a flag in recovered source

```
.js.map -> sourcesContent -> src/config.js has '// flag{...}' ->
pre-flag -> live/artifact proof -> the flag
```

The comment/const is the flag; gate it before submitting.

## Scenario: a thin bundle → dead route

```
entry -> a pure loader, no app code -> no endpoints/secrets ->
the route is dead -> record + move to .git/.env/web-triage
```

A thin bundle is a measured dead end, not a retry.
