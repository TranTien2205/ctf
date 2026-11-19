# Dev build mining — the richer, leaky development bundle

## Why a dev build is gold

A development bundle is built for debugging — sourcemaps on, readable
code, debug flags set, dev endpoints present, `console.log` secrets,
and often the *unminified* original source. A dev build on a deployed
app is a lax-deployment signal and a higher-yield target than prod.

## The dev-build markers

| Marker | Signals a dev build |
|---|---|
| `webpackHotDevClient`, `module.hot`, `webpack-dev-server` | webpack dev-server bundle |
| `sourceURL=` per-module comment | a dev/webpack eval build |
| `//# sourceMappingURL=` on every chunk | maps enabled |
| `NODE_ENV=development`, `__DEV__` | a dev config |
| unminified readable code | a non-optimized build |
| `console.log` calls everywhere | debug logging left on |
| `process.env.DEBUG` | a debug env |

## The dev-build probes

```bash
# dev/staging surface
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/?env=dev"
curl -s -o /dev/null -w '%{http_code}\n' "https://dev.$HOST/"
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/main.dev.js.map"
# dev markers in the prod bundle
grep -oE 'webpackHotDevClient|module\.hot|webpack-dev-server|sourceURL=|__DEV__|NODE_ENV' bundle.js
```

## The `.dev` host pivot

`dev.`, `staging.`, `test.`, `beta.` subdomains often run a dev build —
the same app with sourcemaps on and debug endpoints live. A cert/DNS
probe or a `dev.$HOST` guess may find it. (Only within the supplied
scope.)

## The dev endpoints

A dev build ships dev-only routes — `/debug`, `/test`, `/mock`,
`/_dev`, `/api/test`, `/dev-server` — gated by `NODE_ENV` on the client
but sometimes reachable server-side.

## The `console.log` secret

`console.log(key)`, `console.log(token)`, `console.log('debug:', cfg)` —
a debug print in a dev bundle leaks the value:

```bash
grep -oE 'console\.(log|debug|warn)\([^)]{0,80}' bundle.js | grep -iE 'key|token|secret|pass|flag|cfg|config'
```

## The unminified read

A dev bundle is readable source — `js-beautify` is unnecessary; read it
directly for sinks, keys, routes, the flag. The dev bundle IS the map.
