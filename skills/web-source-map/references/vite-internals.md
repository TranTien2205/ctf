# Vite internals — the ESM bundle shape

## The Vite build output

```
/assets/index-<hash>.js      # the entry chunk (ESM)
/assets/<name>-<hash>.js     # a code-split chunk
/assets/index-<hash>.css     # styles
```

Vite builds ES modules — the output preserves `import`/`export`
structure and `import.meta` refs better than webpack's runtime. It is
often more readable than a webpack bundle.

## The `import.meta` surface

```bash
# Vite env + URL refs
grep -oE 'import\.meta\.[A-Za-z_.]+' bundle.js | sort -u
grep -oE 'import\.meta\.env\.[A-Z_]+' bundle.js | sort -u
grep -oE 'new URL\([^,]+,\s*import\.meta\.url\)' bundle.js
```

`import.meta.env.VITE_*` is the Vite env surface — grep `VITE_` for the
inlined config.

## The ESM import read

`import ... from './chunk-*.js'` — the import graph is visible in the
bundle. The named chunk files map the code-split; the `import()` dynamic
imports name the lazy routes.

```bash
# the chunk imports — the lazy routes
grep -oE 'import\(\s*["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
grep -oE 'from\s+["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
```

## The sourcemap-off default

Vite `build.sourcemap` defaults to `false` in prod — the common case is
no map. String mining is the path; the ESM structure makes the bundle
more readable than webpack's.

## The dev-server leak

A dev Vite build (or `?import`, `/@fs/`, `/@vite/`, `/src/`) leaks the
real source — `/src/main.js`, `/@fs/abs/path` — sometimes even in a
dev-server deployment. Probe `/@fs/` and `/src/` paths on a dev-served
app.

## The `import.meta.glob`

`import.meta.glob('./pages/*.js')` — a dynamic route registration; the
glob pattern names the page set.
