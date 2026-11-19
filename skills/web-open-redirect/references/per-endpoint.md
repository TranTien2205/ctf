# Per-endpoint — each endpoint's redirect surface and the specific check

## `/login` `/signin` `/auth/login` — the post-login landing

```text
the param: next / return / returnTo / goto / continue / back / ret
the flow:  POST the credentials -> on success, 302 to `next`
           on FAILURE, some apps also 302 to `next` (the error-path)
the check: the most-filtered surface — the `//`/`\`/userinfo arms
the value: post-auth landing — the phishing launder + the OAuth hop
```

```bash
curl -si "$BASE/login?next=https%3A%2F%2Fevil.com" | grep -i location
# the error-path variant — a FAILED login with `next`
curl -si -X POST "$BASE/login" -d 'user=x&pass=y&next=https%3A%2F%2Fevil.com' | grep -i location
```

## `/logout` `/signout` — the post-logout landing

```text
the param: next / post_logout_redirect_uri / return
the flow:  logout -> 302 to the destination
the check: often weaker than login — the "logout is harmless" assumption
the value: an OIDC post_logout_redirect_uri is a named surface
```

## `/oauth/authorize` `/sso` `/oidc` — the SSO flow

```text
the param: redirect_uri / callback / RelayState / relay / reply / acs
the flow:  the SSO return — the allowlist-checked surface
the check: the redirect_uri allowlist — a gap launders the code/token
the value: the HIGHEST-value — the web-oauth-sso chain
```

```bash
curl -si "$BASE/oauth/authorize?client_id=X&redirect_uri=https%3A%2F%2Fevil.com" | grep -i location
# the allowlist-bypass — an open-redirect ON the allowlisted domain
curl -si "$BASE/oauth/authorize?client_id=X&redirect_uri=https%3A%2F%2Ftarget.com%2Fredirect%3Fnext%3Dhttps%253A%252F%252Fevil.com" | grep -i location
```

## `/out` `/goto` `/link` `/r` `/u` — the tracker/shortener

```text
the param: url / link / target / dest / u / out / to
the flow:  a click-tracker / link-shortener that 302s to the destination
the check: often unfiltered — the feature IS a redirect
the value: the phishing launder
```

## `/img` `/fetch` `/proxy` `/thumb` `/feed` — the fetcher

```text
the param: url / img / src / uri / feed / file
the flow:  a server-side fetch — the response is fetched CONTENT (SSRF)
           OR a redirect to the URL (open-redirect)
the check: distinguish — is the response the CONTENT or a Location?
the value: the fetcher-follows-Location -> the SSRF chain
```

## `/back` `/previous` `/return` — the Referer-derived

```text
the param: (the Referer header) / back / prev / return
the flow:  a "go back" that 302s to the Referer
the check: forge the Referer header
the value: a header-trust gap
```

```bash
curl -si -H "Referer: https://evil.com" "$BASE/back" | grep -i location
```

## `/error` `/401` `/403` `/404` — the error-path

```text
the param: next / return / url / ref
the flow:  an error -> redirect to a "next"/"return"
the check: the most-missed surface — the error-path redirect often has
           a weaker check than the main flow
```

## `/checkout` `/payment` — the payment-return

```text
the param: successUrl / cancelUrl / failUrl / errorUrl / checkOutUrl / return
the flow:  a payment's post-action destination
the check: the payment-return — the post-payment phishing launder
```

## `/share` `/qr` `/deeplink` — the URL-embedder

```text
the param: url / link / target / data
the flow:  a QR/deep-link/share-link generator
the check: the embedded URL — a laundered link the victim scans/opens
```

## The stored-redirect endpoint — `/set-next`/`/form` + a later flow

```text
step 1: /set-next?next=X    <- the param persists (session/cookie/field)
step 2: /login -> fires     <- the stored fires on a later flow
the check: a single-endpoint sweep misses it — the two-step
```

## The endpoint-to-filter map

| The endpoint | The likely filter | The arms |
|---|---|---|
| `/login` | a `startswith('/')` or an allowlist | `//`, `\`, `%5c`, `@` |
| `/oauth` | a `redirect_uri` allowlist | an open-redirect ON the allowlisted domain |
| `/out`/`/goto` | often none | `https://evil.com` |
| `/img`/`/fetch` | a URL-scheme/host check | the SSRF-chain, the redirect-follow |
| `/back` | a Referer-trust | `Referer: https://evil.com` |
| `/error` | a weaker check | the common arms |

## The per-endpoint record

`endpoint: <path>: <the-param>: <the-carrier>: <the-filter>: <the-verdict>`
