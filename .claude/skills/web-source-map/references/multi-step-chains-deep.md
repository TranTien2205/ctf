# Multi-step chains (deep) — the full chain shapes

## The canonical chain

```
inventory -> map/mine -> name the lead -> verify live -> route -> exploit -> flag
```

The map is link one — the discovery. The rest is the routed class's work.

## Chain: manifest → lazy chunk → admin endpoint → IDOR → flag

```
_buildManifest.js names /admin -> fetch pages/admin-*.js chunk ->
mine its /api/admin/{id} endpoint -> curl /api/admin/1 -> web-idor
reads another user's object -> the flag is in their data
```

The manifest gave the route; the chunk gave the endpoint; IDOR gave the
data.

## Chain: config chunk → key → authenticated reach → gated data → flag

```
config.js carries apiKey -> bundle_miner surfaces it -> curl -H"Auth:
Bearer $K" -> authenticates -> /api/admin returns gated data -> the
flag is behind the gate
```

The config gave the key; auth gave the reach.

## Chain: map → sourcesContent → comment flag → pre-flag

```
.js.map -> sourcesContent -> src/config.js has '// flag{...}' ->
pre-flag the candidate -> live/artifact proof -> the flag
```

The map gave the source; the source gave the flag.

## Chain: feature flag → gated endpoint → direct probe → logic → flag

```
bundle gates /api/debug behind feature.debug -> curl /api/debug
directly -> public response -> the gate was client-only ->
web-logic-flaw works the gate -> the flag
```

The flag named the gate; the server did not check.

## Chain: env inline → internal host → SSRF reach → flag

```
process.env.API_URL = 'http://internal.svc/admin' -> a server-side
fetch surface /proxy?url= reaches it -> web-ssrf pulls internal data ->
the flag is internal
```

The env inline gave the internal host; SSRF gave the reach.

## Chain: route guard → lazy admin chunk → endpoints → flag

```
meta.requiresAuth gates /admin -> the lazy AdminPanel chunk is public
-> mine it for /api/admin/export -> curl it -> public -> the flag
```

The guard hid the page, not the chunk or the endpoint.

## Chain: .map → .git → server source → sink → flag

```
.js.map 200s -> lax-deployment signal -> /.git/HEAD 200s -> git-dump
the tree -> the SERVER source -> a sink the map only hinted at ->
the flag
```

The map signaled lax deployment; the `.git` gave the bigger leak.

## Chain: string → param → injection → flag

```
bundle names ?q= param -> curl "$BASE/x?q=test" -> an injection
oracle -> web-sqli/nosqli extracts -> the flag
```

The bundle named the param; the class exploited it.

## The map's place

The map is always link one — it replaces brute force with the client's
own route table. The chains differ only in which lead the map produced
and which class closes it. A chain that skips the mining step and
guesses endpoints is the same chain, slower.
