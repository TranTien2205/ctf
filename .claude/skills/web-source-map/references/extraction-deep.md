# Extraction (deep) — the grep grammar and the secret filter

## The endpoint grammar

```bash
# quoted absolute paths
grep -oE '"/[A-Za-z0-9_./?=&{}:%@!$~+-]+"' b.js | sort -u
grep -oE "'/[A-Za-z0-9_./?=&{}:%@!$~+-]+'" b.js | sort -u
# template-literal endpoints
grep -oE '`/[A-Za-z0-9_./?=&{}:$-]+`' b.js | sort -u
# the api/version prefixes
grep -oE '"/(api|v[0-9]+|internal|admin|graphql)[A-Za-z0-9_./-]*"' b.js | sort -u
# call-site URLs
grep -oE '(fetch|axios\.[a-z]+)\s*\(\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
# a full URL
grep -oE 'https?://[A-Za-z0-9._/-]+' b.js | sort -u
```

## The param grammar

```bash
# object keys sent to the server
grep -oE '[{,]\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*:' b.js | sort -u
# URLSearchParams / form fields
grep -oE '(append|set|get)\s*\(\s*["'"'"'][a-zA-Z_]+' b.js | sort -u
# a template-literal param
grep -oE '\$\{[a-zA-Z_$][a-zA-Z0-9_$.]*\}' b.js | sort -u
```

## The route grammar

```bash
# react-router / vue-router
grep -oE 'path\s*:\s*["'"'"'][^"'"'"']+' b.js | sort -u
grep -oE 'component\s*:\s*[A-Za-z_$][A-Za-z0-9_$]*' b.js | sort -u
# Next.js page registration
grep -oE '"/[a-z0-9_/-]*"\s*:\s*function' b.js | sort -u
```

## The secret grammar

```bash
# JWT
grep -oE 'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+' b.js
# cloud/API key prefixes
grep -oE '(AKIA|ASIA)[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|ghp_[0-9A-Za-z]{36}|xox[baprs]-[0-9A-Za-z-]+|sk_(live|test)_[0-9A-Za-z]+|pk_live_[0-9A-Za-z]+' b.js
# private key
grep -oE '-----BEGIN [A-Z ]+PRIVATE KEY-----' b.js
# assignment
grep -oE '(api[_-]?key|secret|token|password|client_secret|private_key|auth)["'"'"'\s:=]+["'"'"'][A-Za-z0-9_./+@=-]{6,}' b.js
# env-inlined
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE)_[A-Z_]+' b.js | sort -u
```

## The entropy filter

`bundle_miner --min-entropy` (default ~4.0 bits/char) and
`--min-secret-len` filter candidates. High entropy alone is not enough
— a minified hash is high-entropy and meaningless. The filter is
entropy + context (`--context`/`--lookahead` show the assignment) +
shape (a JWT/`AKIA` prefix). A candidate is verified live.

## The obfuscation-aware pass

String-array obfuscation hides literals behind `_0x1234` lookups —
the strings exist in a packed array at the bundle's head. Extract the
array, decode the lookups, or `strings` the bundle and grep for the
*shape* (`/api/`, `token`, `flag{`). The obfuscator cannot remove the
strings; it only moves them.

## The flag-shape grep

```bash
grep -oE '(flag|ctf|CTF)\{[^}]*\}' b.js
grep -oiE 'flag\s*[:=]\s*["'"'"'][^"'"'"']+' b.js
grep -oE '(TODO|FIXME|HACK|secret|password|key)' recovered/ -r
```
