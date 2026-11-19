# Extraction — pulling the signal out of the bundle and the map

## The tool-first rule

`tools/web/bundle_miner.py` is the sanctioned path — it crawls the
entry page's scripts, fetches each bundle, guesses sibling maps,
reconstructs `sourcesContent`, and inventories endpoints + secret
candidates. Use it before hand-grepping.

```bash
# the whole pipeline on a live entry page
python3 tools/web/bundle_miner.py --url http://TARGET/ --out recovered/

# a bundle already on disk
python3 tools/web/bundle_miner.py --file main.js --map main.js.map --out recovered/

# mine only, no reconstruction
python3 tools/web/bundle_miner.py --url http://TARGET/
```

## The endpoint extraction

The bundle names every endpoint the client calls — the real route
list, not a brute-forced guess:

```bash
# every quoted path that looks like an endpoint
grep -oE '"/[A-Za-z0-9_./?=&{}:-]+"' bundle.js | sort -u
grep -oE "'/[A-Za-z0-9_./?=&{}:-]+'" bundle.js | sort -u
# the api/ prefix patterns
grep -oE '(api|API)[A-Za-z0-9_./-]*' bundle.js | sort -u
# fetch/axios call sites
grep -oE '(fetch|axios\.[a-z]+|\.get|\.post)\(["'"'"'][^"'"'"']+' bundle.js | sort -u
```

`bundle_miner` inventories these automatically — the endpoint list it
emits is the real route table.

## The route extraction

SPA route definitions name every page the app knows — including
unlisted and admin routes:

```bash
# react-router / vue-router route objects
grep -oE 'path:["'"'"'][^"'"'"']+' bundle.js | sort -u
grep -oE 'component:["'"'"']?[A-Za-z_]+' bundle.js | sort -u
# Next.js page chunks
curl -s "$BASE/_next/static/*/…" # the _buildManifest.js lists every route
```

## The feature-flag extraction

```bash
grep -oE '(feature|flag|config|debug|env)[._][A-Za-z_.]+' bundle.js | sort -u
grep -oE '(enable|disable|beta|admin|internal)[A-Za-z_]*' bundle.js | sort -u
```

A `feature.adminPanel` or `config.debug` the front-end hides is a gate
the server may not enforce — a flag to test.

## The secret extraction

```bash
# high-entropy tokens, keys, JWTs
grep -oE '[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+' bundle.js   # JWT
grep -oE '(api[_-]?key|secret|token|bearer|password)["'"'"'\s:=]+[A-Za-z0-9_-]{8,}' bundle.js
grep -oE 'AKIA[0-9A-Z]{16}' bundle.js     # AWS key id
grep -oE '-----BEGIN [A-Z ]+PRIVATE KEY-----' bundle.js
```

`bundle_miner --min-entropy` and `--min-secret-len` tune the secret
candidate filter; `--show-secrets` prints the candidates.

## The source-map reconstruction

When the map exists, `bundle_miner --out DIR` writes the original
`sourcesContent` to disk — the real source:

```bash
python3 tools/web/bundle_miner.py --map main.js.map --out recovered/
ls recovered/   # the original file tree
```

`sourcesContent` is the original commented source — read the real
logic, not the minified strings. A `sources` path that escapes `--out`
(a traversal) is rejected and counted — the map is attacker-controlled.

## The grep-not-read rule

A bundle is megabytes of minified code — never read it whole into
context. Grep for the specific token (endpoint, param, flag, secret)
or let `bundle_miner` inventory it. The exception is a reconstructed
`sourcesContent` file, which is real source and can be read normally.
