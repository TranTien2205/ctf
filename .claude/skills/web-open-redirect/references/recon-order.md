# Recon order — the ordered sweep for a new target

## The 3-command minimal recon

```bash
# 1. the entry page — the redirect vocabulary
curl -s "$BASE/" | grep -oiE '(next|url|redirect|return|goto|out|link|callback)[="]'

# 2. the front-end JS — the client-side sinks
curl -s "$BASE/app.js" | grep -oE 'location\.(href|replace|assign|hash)\s*=\s*[^;]*'

# 3. a known-redirect endpoint — the carrier check
curl -si "$BASE/login?next=/test" | grep -i '^location'
```

## The ordered surface-enumeration

```text
1. the entry page + the bundle   -> the param vocabulary + the JS sinks
2. the redirect-prone endpoints  -> the endpoint inventory
3. the param × endpoint matrix   -> which params reach a Location:
4. the canary on each signal     -> the fingerprint
5. the bypass arms               -> the filter-shape family
6. the client-side + stored + Referer -> the non-Location carriers
7. the chain-route               -> the laundered-trust
```

## The recon-priority — which surface first

```text
1. /login?next=              <- the canonical — the most-common
2. /logout?next=             <- the post-logout — often weaker
3. /oauth/authorize?redirect_uri= <- the OAuth — the highest-value
4. /out?url= /goto?url=      <- the tracker — often unfiltered
5. /error?next=              <- the error-path — the most-missed
6. /back<-Referer            <- the header-carried
7. the stored set-then-fire  <- the two-step
8. the meta/JS/hash          <- the client-side twins
```

## The recon-complete check

```text
the surface is enumerated when:
  - every param name tried on every endpoint
  - every carrier checked
  - every fingerprint's arm-family swept
  - every chain-surface checked
```

## The recon-record

```text
recon: <the-endpoints>: <the-params>: <the-carriers>: <the-signals>`
 — the surface-inventory for the challenge
```
