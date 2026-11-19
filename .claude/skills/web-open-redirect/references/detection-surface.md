# Detection surface — the full surface inventory an agent sweeps

## The redirect-param surface — the ~100-name vocabulary

```text
TIER-1 (the canonical):
  next  url  redirect  redirect_uri  return  returnTo  goto  callback
TIER-2 (the common):
  redir  redirect_url  redirectUrl  returnto  return_url  returnUrl
  dest  destination  target  continue  to  out  view  forward  link
  ref  referer  back  prev  previous  RelayState  relay  reply  acs
TIER-3 (the context-specific):
  post_logout_redirect_uri  logout  signin  signout  auth  oauth  sso
  success  successUrl  cancel  cancelUrl  fail  failUrl  error  errorUrl
  checkOutUrl  image  img  src  uri  feed  file  doc  download  load
TIER-4 (the low-signal):
  ret  from  site  host  path  location  navigate  page  show  landing
  service  content  launch  ready  done  after  before  then  root  home
  start  entry  exit  leave  away  offsite  external  ext  outside  foreign
  jump  hop  bridge  gateway  portal  via  through  via_url  data  end
```

## The endpoint surface — the redirect-prone flows

```text
TIER-1:
  /login /signin /auth/login /logout /signout /auth/logout
TIER-2:
  /oauth/authorize /oauth/callback /sso /saml/acs /oidc/callback
  /oidc/logout /wsfed /ws-federation
TIER-3:
  /out /goto /link /r /u /redirect /return /back /previous
TIER-4:
  /error /401 /403 /404 /checkout /payment/success /payment/cancel
  /register /wizard /form /step2 /share /qr /deeplink /img /fetch /proxy
  /thumb /feed
```

## The carrier surface — the redirect mechanisms

```text
the server-side:
  Location: header   <- the canonical
  Refresh: header    <- a non-Location header
the client-side:
  <meta refresh>     <- the meta-tag
  location.href      <- a JS nav-sink
  location.replace   <- a JS nav-sink
  location.assign    <- a JS nav-sink
  window.location    <- a JS nav-sink
  location = <x>     <- a bare JS nav
  location.hash      <- a fragment-nav
  history.pushState  <- a same-origin path-change
  document.referrer  <- a Referer-read
```

## The stored surface — the two-step carriers

```text
a session field     <- session['next'] set on one endpoint, fired on another
a cookie            <- a Set-Cookie: next=...; the flow reads the cookie
a hidden form field <- a <input name=redirect> carried to the POST
a localStorage      <- the JS reads localStorage.next and navigates
a sessionStorage    <- the JS reads sessionStorage.redirect
```

## The chain surface — the laundered-trust carriers

```text
an OAuth redirect_uri     <- the OAuth-launder
a SAML RelayState         <- the SAML-launder
an OIDC post_logout       <- the logout-launder
a fetcher-follow          <- the SSRF-launder
a javascript:/data: sink  <- the XSS-launder
a bot-visit               <- the bot-launder
a phishing/domain-launder <- the standalone
a %0d%0a in the header    <- the CRLF-launder
```

## The surface-completeness check

```text
the surface is fully swept when:
  - every param name in the vocabulary tried on every endpoint
  - every carrier checked (Location/Refresh/meta/JS/hash/stored/Referer)
  - every fingerprint's arm-family tried
  - every chain-surface checked
a uniform Location: <safe> on every arm = the falsifier
```

## The surface-record

`surface: <the-inventory>: <the-swept>: <the-verdicts>` — the inventory +
what was swept + each surface's verdict.
