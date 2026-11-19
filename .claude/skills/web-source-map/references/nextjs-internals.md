# Next.js internals — the per-route chunk and manifest goldmine

## The Next.js layout

```
/_next/static/<buildId>/_buildManifest.js     # every page route + its chunk
/_next/static/<buildId>/_ssgManifest.js       # the SSG/ISR route list
/_next/static/chunks/main-<hash>.js           # the app shell
/_next/static/chunks/framework-<hash>.js      # react/next runtime
/_next/static/chunks/pages/<route>-<hash>.js  # a page's logic
/_next/static/chunks/<n>.<hash>.js            # a shared/lazy chunk
```

## The `_buildManifest.js` — the route map

The single highest-value Next artifact: it enumerates every page route
and the chunks it loads.

```js
self.__BUILD_MANIFEST = {
  "/_app": ["static/chunks/pages/_app-<h>.js"],
  "/admin": ["static/chunks/pages/admin-<h>.js"],
  "/api/internal": [...],
  "/": [...]
};
```

```bash
BUILD=$(curl -s "$BASE/" | grep -oE '"buildId":"[^"]+"' | head -1 | cut -d'"' -f4)
curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"
```

Every key in the manifest is a route — including `/admin`, `/debug`,
`/internal` routes the UI hides. Fetch each page's chunk; mine it.

## The `__NEXT_DATA__` — serialized props

The entry page embeds `<script id="__NEXT_DATA__">` — serialized
page props, `buildId`, `runtimeConfig`, sometimes server-injected
config and secrets:

```bash
curl -s "$BASE/" | grep -oE '<script id="__NEXT_DATA__"[^>]*>[^<]+' | sed 's/.*>//' | python3 -m json.tool
```

`runtimeConfig`, `props`, and `env` here are a config surface —
server-injected values shipped to the client.

## The `_ssgManifest.js`

Lists the statically-generated/dynamic routes — `/[id]`, `/[slug]` —
naming the param-shape routes (`/:id` → an IDOR-shaped endpoint).

## The API-route boundary

Next.js API routes live at `/api/*` — the manifest's `api/` routes and
the `pages/api/` chunk names name them. A `/api/internal` in the
manifest is a real server endpoint, not a client route.

## The middleware + edge config

`/_next/static/chunks/middleware` / `edge-runtime` — the middleware
bundle may carry auth/route logic and edge config (keys, allowed
origins). Worth mining on App-Router / middleware-heavy apps.

## The per-page-chunk rule

The interesting endpoint is almost always in a *page chunk*
(`pages/admin-*.js`), not `main`. The manifest's route list is the
complete page inventory — fetch every page chunk, not just `main`.

## The Next-specific strings

`getServerSideProps`, `getStaticProps`, `getInitialProps`, `router.push`,
`useRouter`, `api/`, `NEXT_PUBLIC_*` — each is a lead to a server
fetch, an env value, or a route.
