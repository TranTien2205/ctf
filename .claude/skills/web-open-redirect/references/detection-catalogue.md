# Detection catalogue — every detection signal, catalogued

## The param-name signals — the vocabulary catalogue

```text
PRIMARY (the canonical):
  next  url  redirect  redirect_uri  return  returnTo  goto  dest  target
SECONDARY (the common):
  continue  to  out  view  callback  forward  link  ref  destination
  returnto  return_url  redirect_url  redirectUrl  RelayState
TERTIARY (the context-specific):
  post_logout_redirect_uri  relay  reply  acs  successUrl  cancelUrl
  failUrl  errorUrl  checkOutUrl  image  img  src  uri  feed  file  doc
  back  prev  previous  referer  site  host  path  navigate  page
WEAK (the low-signal):
  ret  from  landing  service  load  download  content  launch  ready
  done  after  before  then  root  home  start  entry  exit  leave  away
```

## The endpoint signals — the surface catalogue

```text
HIGH-VALUE:
  /login /signin /auth/login          <- the post-auth landing
  /logout /signout                    <- the post-logout
  /oauth/authorize /oauth/callback    <- the OAuth flow
  /sso /saml/acs /oidc/callback       <- the SSO flow
  /out /goto /link /r /u              <- the tracker
MEDIUM:
  /redirect /return /back /previous   <- the generic redirect
  /error /401 /403 /404               <- the error-path
  /checkout /payment/success          <- the payment-return
LOWER:
  /img /fetch /proxy /thumb /feed     <- the fetcher (SSRF-twin)
  /share /qr /deeplink                <- the URL-embedder
```

## The carrier signals — the redirect-mechanism catalogue

```text
Location: header      <- the canonical 3xx carrier
Refresh: header       <- a non-Location header carrier
<meta refresh>        <- the client-side tag carrier
location.href/replace/assign <- the client-side JS carrier
location.hash         <- the fragment carrier (same-page unless re-read)
history.pushState     <- a same-origin path-change (not cross-origin)
document.referrer     <- a client-side Referer-read
```

## The fingerprint signals — the Location-shape catalogue

```text
Location: <canary-verbatim>           <- CANDIDATE — the oracle
Location: <canary-scheme-relative>    <- CANDIDATE — //evil.com
Location: <canary-subdomain>          <- CANDIDATE — target.com.evil.com
Location: <canary-substring>          <- CANDIDATE — evil.com/target.com
Location: <safe-relative>             <- a safe arm — forced-relative
Location: <safe-absolute>             <- a safe arm — allowlisted
Location: <relative-no-scheme>        <- a negative — resolves same-origin
Location: <javascript:>               <- a scheme-candidate — browser-split
Location: <data:>                     <- a scheme-candidate
no Location / 200 render              <- a weak-negative — wrong param
400 / 422                             <- a format-reject — a different param
```

## The status signals — the redirect-type catalogue

```text
302 Found          <- the common; the method drops on the follow
301 Moved          <- the permanent
303 See Other      <- the REST-shape
307 Temporary      <- keeps the method
308 Permanent      <- keeps the method
200 + meta         <- the client-side twin
200 + JS-nav       <- the client-side twin
```

## The chain signals — the laundered-trust catalogue

```text
the OAuth allowlist on a domain with an open-redirect  -> the OAuth chain
a fetcher that follows Location                        -> the SSRF chain
a javascript:/data: reaching a sink                    -> the XSS chain
a bot that visits target.com URLs                      -> the bot chain
a %0d%0a reaching the Location header                  -> the CRLF chain
a standalone canary + the phishing shape               -> the class's answer
```

## The falsifier signals — the class-closing catalogue

```text
Location: <safe> on EVERY canary + bypass arm  -> the class falsifier
no Location on every param                     -> a weak-negative sweep
the meta/JS escaped on every carrier           -> the client-side-twin closed
the scheme rejected on every scheme-arm        -> the scheme-surface closed
```

## The catalogue-record

`catalogue: <the-signal-family>: <the-signal> -> <the-next-probe>`
