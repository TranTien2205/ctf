# Bundle mining (deep) — reading a minified bundle systematically

## The bundle anatomy

A webpack bundle is a module registry — `(function(){var modules={id1:fn1,
id2:fn2,...}; __webpack_require__(entry)})`. Each module fn is one
original file, minified. The interesting ones are the *application*
modules, not `node_modules` runtime.

## The module-boundary read

```bash
# find module boundaries — the per-file logic
grep -oE '(function|\{)\s*\(\s*\w+\s*,\s*\w+\s*,\s*__webpack_require__\s*\)' bundle.js
# each module's exported shape hints at its role
```

When the bundle is not obfuscated, `js-beautify`/`prettier` reformats it
into near-source — beautify-then-read is the middle path between grep
and a full map.

```bash
npx js-beautify bundle.js > bundle.pretty.js 2>/dev/null || python3 -c "import jsbeautifier" 2>/dev/null
# or prettier
npx prettier --write bundle.js 2>/dev/null
```

## The call-graph read

Find an endpoint, then read what calls it and what it feeds:

```bash
# the endpoint's context — the function that calls it
grep -oE '.{120}/api/internal.{120}' bundle.js
# the call-site
grep -oE '(fetch|axios\.[a-z]+|\.request)\s*\([^)]*' bundle.js | grep -i 'internal\|api'
```

The call-site shows the params the client sends and the response it
expects — the server's contract.

## The config-block read

The build inlines config into a recognizable block:

```bash
# process.env / DefinePlugin inlined values
grep -oE 'process\.env\.[A-Z_a-z]+' bundle.js | sort -u
grep -oE '\{[^{}]*"(apiUrl|apiKey|baseUrl|endpoint|secret|token|debug|env)"[^{}]*\}' bundle.js
# a config object literal
grep -oE '(config|env|settings|defaults)\s*[:=]\s*\{[^{}]{20,}' bundle.js
```

## The route-table read

```bash
# react-router <Route path=...> / router config
grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' bundle.js | sort -u
grep -oE '(component|element|lazy|import)\s*:\s*[A-Za-z_$.(]+' bundle.js | sort -u
# a routes array
grep -oE '(routes|ROUTES|Paths)\s*[:=]\s*\[[^\]]{20,}' bundle.js
```

## The auth/read read

```bash
# where the token lives and how it is sent
grep -oE '(localStorage|sessionStorage|document\.cookie)\S{0,40}' bundle.js | sort -u
grep -oE '(Authorization|Bearer|X-[A-Za-z-]*Token|api[_-]?key)["'"'"'\s:=]+' bundle.js | sort -u
```

## The dead-code read

The bundle ships dead code — commented-out routes, `if(false)` blocks,
feature-flagged-off paths, dev-only endpoints. A `feature.X` check that
gates a route the server does not is the classic logic-flaw lead:

```bash
grep -oE 'if\s*\(\s*[^)]*(feature|flag|debug|beta|internal|admin)[^)]*\)' bundle.js
grep -oE '(feature|flags|config)\.[a-zA-Z_]+' bundle.js | sort -u
```

## The sink read in recovered/beautified source

Once the code is readable, hunt the sink the challenge wants:

```bash
grep -niE 'eval|innerHTML|dangerouslySetInnerHTML|deserialize|exec|subprocess|render|file_get|open\(|fetch\(|\.post\(|\.get\(' recovered/ pretty.js
```

Each sink names a bug class — route it.
