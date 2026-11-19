# Per-vector — the recon angles the map opens

## The endpoint vector

Every endpoint string is a server surface the UI may not expose —
`/api/internal`, `/admin/export`, `/v2/debug`. Each is a target for its
own class once verified live. The vector: the client names the real
route table, replacing brute force.

## The secret vector

A key, token, JWT, or credential in client source is a live auth path —
if it verifies, it unlocks whatever it authenticates to. The vector:
the client shipped the credential; verify and use it.

## The flag vector

A `feature.*`/`config.*`/`flags.*` gate the client checks but the
server may not enforce. Setting the flag (a param, a header, a
localStorage key the client reads) reaches the gated behavior.

## The source vector

`sourcesContent` is the original commented source — sinks, logic, and
secrets visible as the dev wrote them. The vector: read the real code,
find the sink, route to its class.

## The internal-host vector

`http://internal.svc`, `api.internal.*`, a webhook URL — a host the
client calls but the browser cannot reach. An SSRF surface reaches it.

## The structure vector

`sources` file names alone (no content) — `src/api/auth.js`,
`src/config/secrets.js`, `src/admin/` — map the app's internal layout.
The names are probe targets: the same paths may be hosted
(`/src/config/secrets.js`) or hint at a `file-read` target.

## The manifest vector

`_buildManifest.js` / `asset-manifest.json` name every route and asset
the build ships — a complete inventory the UI never displays.

## The adjacent-disclosure vector

A host that ships its `.map` often ships `.git`, `.env`, backups —
the map is a signal the deployment is lax. The vector: the map's
presence probes for the broader info-disclosure surface.
