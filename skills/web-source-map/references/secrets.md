# Secrets — finding and handling keys, tokens, and credentials

## What counts as a secret here

Anything that grants access a visitor should not have:

- **API keys** — `api_key`, `apikey`, `AKIA...`, `sk_live_`, `pk_live_`
- **tokens** — JWTs, OAuth tokens, bearer tokens, session tokens
- **signing keys** — a JWT secret, an HMAC key, a private key block
- **credentials** — `password`, `passwd`, `secret`, `client_secret`
- **internal URLs** — an internal service host, a webhook URL, a
  database connection string

## The entropy filter

A real secret is high-entropy — a long run of unpredictable characters.
`bundle_miner --min-entropy` and `--min-secret-len` tune the candidate
filter; the defaults catch real keys without drowning in variable
names:

```bash
python3 tools/web/bundle_miner.py --file bundle.js \
  --min-entropy 4.0 --min-secret-len 20 --show-secrets
```

## The pattern set

```bash
# JWTs — three base64url segments
grep -oE 'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+' bundle.js
# AWS access key id
grep -oE 'AKIA[0-9A-Z]{16}' bundle.js
# common key prefixes
grep -oE '(sk|pk|rk|xox[baprs]|ghp|gho|glpat|AIza)[A-Za-z0-9_-]{10,}' bundle.js
# private key blocks
grep -oE '-----BEGIN [A-Z ]+PRIVATE KEY-----' bundle.js
# assignment patterns
grep -oE '(api[_-]?key|secret|token|password|client_secret|private[_-]?key)["'"'"'\s:=]+["'"'"'][A-Za-z0-9_./+-]{8,}' bundle.js
```

## The false-positive problem

A bundle is full of secret-*looking* strings — minified variable names,
class names, hashes, random ids. The filter:

- **context** — `apiKey = "..."` or `Authorization: Bearer ...` is
  stronger than a bare high-entropy string
- **shape** — a JWT's `eyJ` prefix, an `AKIA` prefix, a `-----BEGIN`
  block — structural, not just entropy
- **place** — a `config.js`/`secrets.js`/`env.js` source file is
  stronger than a random chunk

`bundle_miner`'s `--context` and `--lookahead` widen the capture around
a hit to show the assignment it lives in — the context is the
strongest signal.

## The verification rule

A secret candidate is a *candidate* — verify it works before treating
it as a finding:

```bash
# does the key authenticate?
curl -s -H "Authorization: Bearer $CAND" "$BASE/api/me"
# does the JWT decode to something real?
echo "$CAND" | cut -d. -f2 | base64 -d 2>/dev/null
```

A dead key is not a finding; a live one routes to
`../web-auth-session/` for what it unlocks.

## The route after a find

| Found | Route to |
|---|---|
| a live API key / token | `../web-auth-session/` — what it authenticates |
| a JWT secret | `../web-auth-session/` — forge the session |
| a private key | `../web-auth-session/` / `../file-read-primitives/` |
| an internal URL | `../web-ssrf/` — can the server reach it |
| an admin route | `../web-idor/` / `../web-logic-flaw/` |
| a feature flag | `../web-logic-flaw/` — is the gate server-side |

## The honest record

Record the candidate, its source file, and whether it verified live —
a secret that never verified is a note, not a finding. Do not present
a high-entropy string as a leaked credential without the live check.
