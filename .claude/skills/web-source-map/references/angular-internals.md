# Angular internals — the lazy-module bundle shape

## The Angular CLI output

```
/main.<hash>.js           # the app + root module + root routes
/runtime.<hash>.js        # the webpack runtime (skip)
/polyfills.<hash>.js      # polyfills (skip)
/<n>.<hash>.js            # a lazy-loaded feature module
/styles.<hash>.css
```

Angular lazy-loads feature modules into numbered chunks — the admin
module is often a lazy chunk the UI loads on a route it hides.

## The lazy-module rule

The interesting endpoint is most often in a lazy module (`[n].hash.js`)
loaded on a gated route — `/admin`, `/internal`. The root `main` holds
the routes table; the lazy chunk holds the gated logic.

```bash
# every lazy chunk — the loadChildren pattern
grep -oE 'loadChildren[^,}]*' bundle.js | sort -u
grep -oE 'import\(\s*["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
# fetch every numbered chunk
for n in $(seq 0 20); do curl -s -o /dev/null -w "$n %{http_code}\n" "$BASE/$n.$HASH.js"; done
```

## The routes table

```bash
# RouterModule.forRoot/forChild route defs
grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
grep -oE '(canActivate|canLoad|component|loadChildren)\s*:\s*[A-Za-z_.(]+' bundle.js | sort -u
```

`canActivate`/`canLoad` guards are *client-side* — the lazy module and
its endpoints are still shipped; the guard is bypassable if the server
does not check.

## The service layer

`HttpClient.get('/api/...')`, `.post(...)`, `http://`, `apiUrl` — the
endpoints the services call:

```bash
grep -oE '(this\.http|http)\.(get|post|put|delete|patch)\(["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
grep -oE '(apiUrl|baseUrl|endpoint|API_URL)\s*[:=]\s*["'"'"'`][^"'"'"'`]+' bundle.js
```

## The environment file

`environment.prod.ts`/`environment.ts` compile into the bundle —
`environment.apiUrl`, `production:`, `apiKey:` — the inlined config:

```bash
grep -oE '(environment|production|apiKey|apiUrl|firebase)[^,}]{0,60}' bundle.js | sort -u
```

## The AOT/observe

Angular AOT-compiles templates — the template HTML is in the bundle as
strings, which can carry hidden routes, comments, and flag text.
