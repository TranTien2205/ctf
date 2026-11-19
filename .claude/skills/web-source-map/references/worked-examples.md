# Worked examples — complete passes, narrated

## Example 1: a Next.js app ships a `.map`

1. `curl $BASE/` → a `<script id="__NEXT_DATA__">` + `"/_next/static/…"`
   → Next.js. The `buildId` is `XYZ`.
2. `curl $BASE/_next/static/XYZ/_buildManifest.js` → the route table:
   `/`, `/about`, `/admin`, `/api/internal`. `/admin` + `/api/internal`
   are the leads.
3. `curl $BASE/_next/static/chunks/main-*.js` → `sourceMappingURL` on
   the tail → `main-*.js.map` returns `200 application/json`
   `{"version":3` → a real map.
4. `bundle_miner --url $BASE/ --out recovered/` → `sourcesContent`
   reconstructs `pages/admin.tsx`, `lib/api.ts`, `config/env.ts`.
   `env.ts` carries `const API_KEY = "sk_live_…"`.
5. Verify: `curl $BASE/api/internal` → `200` `{users:[…]}` — a live
   admin API, no auth check → route to `web-idor`. `curl -H
   "Authorization: Bearer sk_live_…" $BASE/api/admin` → `200` — the key
   is live → route to `web-auth-session`.
6. Record: `/api/internal` live, `sk_live_` live, `/admin` route
   client-gated → `web-idor` + `web-auth-session`.

The map was the recon; the `curl` verify made the leads findings.

## Example 2: a webpack SPA, no map, a lazy admin chunk

1. `curl $BASE/` → `<script src="/static/js/main.a1b2.js">` +
   `webpackChunk` — webpack, no `<script>` for the admin chunk.
2. `curl $BASE/asset-manifest.json` → `main`, `2.chunk`, and
   `admin.chunk.js` — a lazy chunk `main` never named.
3. `main.js.map` → `404`; `admin.chunk.js` `sourceMappingURL` → none.
   No map → string mine.
4. `strings admin.chunk.js | grep -oE '"/api/[^"]*"'` →
   `"/api/export"`, `"/api/backup"`, `"/api/users/{id}"`.
   `curl $BASE/api/export` → `200` — a live export endpoint, gated only
   by the client's `isAdmin` check → `web-logic-flaw`/`web-idor`.
5. `strings admin.chunk.js | grep -E 'role|is_admin'` →
   `{"role":"user", is_admin:false}` — the client's auth state; a
   `role`/`is_admin` param the server may bind → `web-mass-assignment`.

No map — the lazy chunk + the string mine carried the pass.

## Example 3: a Vite SPA, secrets in `import.meta.env`

1. `curl $BASE/` → `<script type="module" src="/assets/index-*.js">`
   → Vite.
2. `index-*.js.map` → `404`. String mine:
   `grep -oE 'import\.meta\.env\.[A-Z_]+|VITE_[A-Z_]+\s*[:=]'` →
   `VITE_API_URL` (the API base) and `VITE_SENTRY_DSN` (a publishable
   DSN — a candidate, not a secret).
3. `grep -oE '"/api/[^"]*"|fetch\([^)]*'` → `/api/users?role=`,
   `/api/debug`, a `?url=` fetch param.
4. Verify: `VITE_SENTRY_DSN` → publishable, dead. `/api/debug` → `403`
   stays `403` → server-enforced, dead. `?url=` → `web-ssrf`.
   `?role=` → `web-mass-assignment`.
5. Record: 4 leads, 0 secrets-live, 2 live endpoints → `web-ssrf` +
   `web-mass-assignment`; 1 publishable secret + 1 dead gate →
   negatives.

A clean "no secret, two live endpoints" pass — the map was still the
recon that surfaced them.

## The pattern in all three

Inventory → map-or-string → mine every chunk → verify each lead →
route. The bundle is read like a spec; the live check makes a string
into a finding; the dead lead is a recorded negative, not a retry.
