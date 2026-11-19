# Vue internals — the Vue CLI bundle shape

## The Vue CLI output

```
/js/app.<hash>.js              # the application
/js/chunk-vendors.<hash>.js    # the dependencies (skip)
/js/<route>.<hash>.js          # a lazy route chunk
/css/app.<hash>.css
```

`app` is the application + route table; `chunk-vendors` is
`vue`/`vue-router`/`axios` — skip it; per-route chunks hold the page
logic.

## The vue-router read

```bash
# the routes table
grep -oE '(path|name|component)\s*:\s*["'"'"'`]?[A-Za-z0-9_./()-]+' bundle.js | sort -u
grep -oE '(routes|router)\s*[:=]\s*\[[^\]]{20,}' bundle.js
# a lazy component import names its chunk
grep -oE 'import\(\s*["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
```

The route table names every page — `/admin`, `/internal`, `/secret` —
including `meta: { requiresAuth: true }` gated routes whose code is
shipped anyway.

## The `meta` gate

```js
{ path: '/admin', meta: { requiresAuth: true, role: 'admin' } }
```

A `meta.requiresAuth`/`role` is a *client-side* guard — the component
and its endpoints are still shipped. The `meta` field names the gate
the client checks; the server may not.

## The `VUE_APP_` env

`VUE_APP_*` env values inline into the bundle — grep `VUE_APP_` +
`process.env.VUE_APP_` for the config surface.

## The axios/fetch layer

`axios.create({baseURL: ...})`, `this.$http`, `axios.get('/api/...')` —
the API base and every endpoint the client calls:

```bash
grep -oE 'baseURL\s*:\s*["'"'"'`][^"'"'"'`]+' bundle.js
grep -oE '(axios|\$http)\.[a-z]+\(["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
```

## The store/state read

`store.state`, `getters`, `mutations` — the client state may carry
`isAdmin`, `token`, `user` — a client-side privilege flag the server
may trust.
