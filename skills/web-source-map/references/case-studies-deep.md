# Case studies (deep) — the worked recon shapes

## Catalogue note

Standard published shapes — no local verified solve yet. Record a real
solve to promote the class.

## Study 1: the Next.js manifest → hidden admin

An app shows a login page. `/_next/static/<buildId>/_buildManifest.js`
enumerates `/admin`, `/api/internal`, `/debug` — routes no link reaches.
Fetching `pages/admin-<hash>.js` yields the admin endpoints; probing
`/api/internal` returns data the UI gated. The manifest was the route
map; the page chunk was the spec; the endpoint was the target.
**Chain**: manifest → page chunk → endpoint → `web-idor`/`web-logic-flaw`.

## Study 2: `config.js` → a live key

A Vue app's `config.js` chunk carries `apiKey: "sk_live_..."` and
`apiUrl: "https://api.internal.example.com"`. `bundle_miner
--show-secrets` surfaces the candidate; the live check authenticates to
`/api/me`. The key unlocks the gated surface; the internal URL routes
to `web-ssrf`. **Chain**: config chunk → key candidate → live verify →
`web-auth-session` → the gated endpoint.

## Study 3: `sourcesContent` → the flag

A `main.[hash].js.map` with `sourcesContent` reconstructs
`src/config.js` — `// flag{...}` in a comment, or `const FLAG`. The map
is the recovery; the comment is the flag. `pre-flag` gates it.
**Chain**: `.map` → `sourcesContent` → comment/const → `pre-flag`.

## Study 4: the lazy admin chunk → the gated surface

A React SPA's `main` names a lazy `import('./AdminPanel')`. Fetching
`5.<hash>.chunk.js` (the admin module) reveals `/api/admin/export`,
`/api/internal/dump` — endpoints `main` never showed. The lazy chunk is
public; the *load* was role-gated client-side. **Chain**: lazy
`import()` → admin chunk → admin endpoints → `web-idor`/`web-logic-flaw`.

## Study 5: `feature.debug` → the gated behavior

The bundle gates `/api/debug` behind `if (feature.debug)`. Probing the
endpoint directly returns the debug data — the gate was client-side,
the server did not check. The flag named the gate; the endpoint was
always reachable. **Chain**: flag name → gated endpoint → direct probe
→ `web-logic-flaw`.

## Study 6: the `.map` → `.git` pivot

`.js.map` returns the map; a `/.git/HEAD` probe returns `ref:` — the
same lax deployment ships the git repo. The `.git` recovers the *server*
source, richer than the map. **Chain**: map → lax-deployment signal →
`.git` → full source → `web-info-disclosure`.

## Study 7: `process.env` → an internal URL

The bundle's `process.env.API_URL` inlines
`http://internal.svc:8080/admin` — an internal host the client calls. A
server-side fetch surface (`/proxy?url=`) reaches it. **Chain**: env
inline → internal host → SSRF reach → `web-ssrf`.

## Study 8: the client-only flag → the public endpoint

`meta.requiresAuth` gates `/admin` — but the component and its
`/api/admin` endpoint are shipped. Probing the endpoint directly (as a
guest) returns data — the guard was client-only. **Chain**: route guard
→ gated endpoint → direct probe → `web-idor`/`web-logic-flaw`.
