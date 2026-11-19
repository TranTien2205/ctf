# Detection matrix — signal → state → action

| Signal in entry/bundle | Indicates | Action |
|---|---|---|
| `/_next/static/` | Next.js | fetch `_buildManifest.js` for the route list |
| `/static/js/main.[hash].js` | CRA/webpack | fetch `main.[hash].js.map` |
| `/assets/index-[hash].js` | Vite | mine strings; map rare in prod |
| `webpackChunk`/`__webpack_require__` | webpack | enumerate every chunk |
| `//# sourceMappingURL=` | a map exists | fetch the `.map` |
| `data:application/json;base64` at tail | an inline map | base64-decode the map |
| `__NEXT_DATA__` | Next serialized props | parse for config/secrets |
| `/js/app.[hash].js` + `chunk-vendors` | Vue CLI | mine `app.` and route chunks |
| `runtime.`+`polyfills.`+`main.` | Angular | mine lazy module chunks |
| `sw.js`/service worker | a precached app | mine the precache manifest |
| `.map` 200 + `application/json` | a real map | reconstruct `sourcesContent` |
| `.map` 200 + `text/html` | a catch-all | not a map — string mine |
| `.map` 404 everywhere | no map | string mine only |
| high-entropy string | a secret candidate | `--show-secrets`, verify live |
| `api/`, `/admin`, `/internal` string | an endpoint claim | probe the route live |
| `feature.`/`config.`/`flags.` | a gate flag | find its endpoint, test the gate |
| `http://internal`, `api.internal` | an internal host | SSRF reach probe |
| `const FLAG`, `flag{` in source | a flag candidate | `pre-flag` gate |

## The decision tree

```
entry page -> script list -> fetch all bundles
  |
  +-- .map exists? --yes--> reconstruct sourcesContent -> read real source
  |                    |
  |                    no--> string mining on every bundle
  |
  +-- strings found?
       |
       +-- endpoints -> verify live -> route to class
       +-- secrets   -> verify live -> web-auth-session
       +-- flags     -> find endpoint -> web-logic-flaw
       +-- internal  -> SSRF reach
       +-- flag shape-> pre-flag gate
```

## The falsifier row

| All bundles mined, strings opaque, no endpoints/secrets | route dead | record negative |
| `.map` 404 + no `sourceMappingURL` | no map | string mine, or route dead if strings opaque too |
