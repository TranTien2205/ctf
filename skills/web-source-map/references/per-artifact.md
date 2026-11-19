# Per-artifact — what each bundle artifact yields

## The artifact index

| Artifact | Where | Yields |
|---|---|---|
| `main.js`/`index-*.js`/`app.*.js` | the entry bundle | routes, env, core endpoints, feature flags |
| `2.chunk`/lazy/`pages/*`/`views/*` | code-split module | the hidden/lazy route's endpoints |
| `admin.chunk`/`*.admin.*` | a gated module | the gated surface — usually the gold |
| `vendor.js`/`runtime.js`/`manifest.js` | the runtime/vendor | usually skip — boilerplate + framework |
| `_buildManifest.js`/`asset-manifest.json` | the build manifest | the complete route + chunk inventory |
| `sw.js`/`precache-manifest.*.js` | the service worker | every cached route+asset, an offline surface |
| `main.js.map`/`*.js.map` | the `.map` | `sourcesContent` → the real source |
| `*.css.map`/`*.css` | the style map | source paths, sometimes a `/* */` comment secret |
| `__NEXT_DATA__`/`window.__NUXT__`/`window.__` | inlined state/config | env, flags, runtimeConfig, pre-rendered data |
| `config.js`/`env.js`/`settings.js` | a config bundle | the densest secret/flag block |
| `webpack.config.js`/`vite.config.*` | a shipped build file | dev-only source |
| `.git/`/`.env`/backups | adjacent artifact | the bigger leak when `.map` is shipped |
| `package.json`/`composer.json` | a manifest artifact | dependency + script hints |
| `robots.txt`/`sitemap.xml` | a crawl artifact | the named-but-unlinked paths |

## The yield priority

Highest yield per byte: a `.map` `sourcesContent` (everything),
`config.js`/`env.js` (secrets), `__NEXT_DATA__`/`window.__` (env+flags),
a lazy/admin chunk (hidden endpoints), the manifest (the inventory).

## The artifact → lead type map

| Artifact | Lead type |
|---|---|
| lazy/admin chunk | hidden endpoint + client gate |
| config/env/`__NEXT_DATA__` | a secret/flag candidate |
| `.map` `sourcesContent` | everything — incl. comments + dead code |
| `sources` path | a hosted source path |
| `sw.js` | an offline-cached surface |
| `.git`/`.env` | a bigger disclosure |
| `robots.txt`/`sitemap.xml` | unlinked paths |
