# Secrets catalogue — the full candidate pattern set

## Credential patterns

```bash
# JWTs — three base64url segments
grep -oE 'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+' b.js
# AWS
grep -oE '(AKIA|ASIA|AGPA|AIDA|AROA)[0-9A-Z]{16}' b.js
grep -oE 'aws(.{0,20})?(secret|key)["'"'"'\s:=]+["'"'"'][A-Za-z0-9/+=]{20,}' b.js
# cloud/API
grep -oE 'AIza[0-9A-Za-z_-]{35}' b.js                              # Google
grep -oE 'AIzaSy[\w-]{33}' b.js
# git hosts
grep -oE '(ghp|gho|ghs|ghu|ghr)_[0-9A-Za-z]{36,}' b.js             # GitHub
grep -oE 'github_pat_[0-9A-Za-z_]{22,}' b.js
grep -oE 'glpat-[0-9A-Za-z_-]{20,}' b.js                           # GitLab
# messaging
grep -oE 'xox[baprs]-[0-9A-Za-z-]{10,}' b.js                       # Slack
grep -oE 'discord(app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+' b.js
# payments
grep -oE '(sk|pk|rk)_(live|test)_[0-9A-Za-z]+' b.js                # Stripe
grep -oE 'sq0[a-z]{3}-[0-9A-Za-z_-]{20,}' b.js                     # Square
# generic
grep -oE '(api[_-]?key|apikey|secret|token|password|passwd|client_secret|private_key|access_token|auth_token|bearer)["'"'"'\s:=]+["'"'"'][A-Za-z0-9_./+@=-]{6,}' b.js
```

## Private-key blocks

```bash
grep -oE '-----BEGIN [A-Z ]+PRIVATE KEY-----' b.js
grep -rnoE '-----BEGIN [A-Z ]+PRIVATE KEY-----' recovered/
```

## Connection strings

```bash
grep -oE '(postgres|postgresql|mysql|mongodb(\+srv)?|redis|amqp|mssql|sqlite)://[^"'"'"']+' b.js
grep -oE '(Server|Data Source|Host)=[^;]+;' b.js
```

## Internal URLs/hosts

```bash
grep -oE 'https?://[a-z0-9.-]*(internal|\.svc|\.local|\.intra|\.corp|10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.|localhost|127\.)[^"'"'"' ]*' b.js
```

## Env/config inlines

```bash
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE|GATSBY|NUXT|ANGULAR)_[A-Z_]+' b.js | sort -u
grep -oE 'process\.env\.[A-Z_a-z]+' b.js | sort -u
grep -oE 'import\.meta\.env\.[A-Z_]+' b.js | sort -u
```

## The flag shape

```bash
grep -oE '(flag|ctf|CTF|FLAG)\{[^}]*\}' b.js
grep -rnoE '(flag|ctf)\{[^}]*\}' recovered/
grep -oiE '(const|let|var)\s+(FLAG|flag|secret)\s*=\s*["'"'"'][^"'"'"']+' recovered/
```

## The publishable exclusion

`pk_live_`, `NEXT_PUBLIC_*`, `REACT_APP_*` public config, a Firebase
`apiKey`, a public `appId` — meant to be public; a leak only if it
unlocks more than the public surface. Verify before claiming.

## The context check

`bundle_miner --context`/`--lookahead` widens the capture around a hit
— the assignment it lives in is the strongest signal. A secret-looking
string in a comment, a variable name, or a hash position is not a
credential.
