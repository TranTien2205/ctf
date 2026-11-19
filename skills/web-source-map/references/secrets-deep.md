# Secrets (deep) — the full candidate taxonomy and verify protocol

## The candidate taxonomy

| Class | Shape | Risk |
|---|---|---|
| JWT | `eyJ...\....\....` (3 base64url segs) | a live session/token |
| AWS key id | `AKIA[0-9A-Z]{16}` | cloud credential |
| Stripe | `sk_live_`, `pk_live_`, `rk_live_` | payment key |
| GitHub | `ghp_`, `gho_`, `ghs_`, `github_pat_` | repo token |
| GitLab | `glpat-` | repo token |
| Slack | `xox[baprs]-` | workspace token |
| Google | `AIza[0-9A-Za-z_-]{35}` | API key |
| private key | `-----BEGIN ... PRIVATE KEY-----` | signing/decryption |
| generic secret | `apiKey`/`secret`/`token`/`password`/`client_secret` assign | app credential |
| env-inlined | `process.env.*`, `REACT_APP_*`, `NEXT_PUBLIC_*` | build config |
| connection string | `postgres://`, `mongodb://`, `redis://`, `mysql://` | a database |
| webhook/URL | `hooks.slack.com`, `discord.com/api/webhooks` | a callable URL |

## The three-signal filter

A candidate is worth verifying only when it passes three signals:

1. **entropy** — high enough to not be a variable name (`--min-entropy`)
2. **context** — sits in an assignment/send position, not a comment or a
   minified identifier (`--context`/`--lookahead`)
3. **shape** — a structural prefix (`eyJ`, `AKIA`, `sk_`, `-----BEGIN`)
   or a named field (`apiKey:`, `secret:`)

A bare high-entropy string with no context is usually a hash or a
minified id — the common false positive.

## The verify protocol

```bash
# a JWT — decode it first
echo "$CAND" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool
# is it a real session? does it carry a user/role/exp?

# an API key / bearer token — does it authenticate?
curl -s -H "Authorization: Bearer $CAND" "$BASE/api/me"
curl -s "$BASE/api/me?api_key=$CAND"
curl -s -H "X-API-Key: $CAND" "$BASE/api/me"

# a connection string — is the host reachable / does it name a db?
# (do NOT connect to a real db — note the string, route to ssrf/file-read)
```

A candidate is a finding only when the live check proves it — the JWT
decodes to a real claim, the key returns data, the credential
authenticates.

## The publishable-key trap

`pk_live_`, a Firebase `apiKey`, a `NEXT_PUBLIC_*` value — these are
*intended* public; the client needs them to run. They are not leaks
unless they grant more than the public surface. The check: does the key
unlock something a guest cannot do? If not, it is a public config value,
not a finding — record it as such.

## The dead-key outcome

A candidate that fails every verify is a dead key — record it (source
file + the failed check) so the next solver does not re-verify it. A
dead key is not a finding.

## The internal-URL subclass

`postgres://`, `mongodb://`, `internal.svc`, `api.internal.*` — these
are not credentials but *internal targets*; an SSRF surface reaches
them. Route to `web-ssrf`, not `web-auth-session`.

## The flag-adjacent case

A `const FLAG`, a `flag{` literal in the bundle or recovered source is
a *candidate* — `pre-flag` it, prove it against a live/artifact
response. The same candidate-discipline as a secret.
