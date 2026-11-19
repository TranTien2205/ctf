# Parameter inventory — the complete list of redirect-param names

## The core list — the 20 highest-signal names

```text
next  url  redir  redirect  redirect_uri  redirect_url  return  returnTo
returnto  return_url  goto  dest  destination  target  continue  out
view  callback  to  forward
```

## The full sweep list — feed to `redirect_probe.py --param` or the sweep

```text
next  url  redir  redirect  redirect_uri  redirect_url  redirectUrl
redir_uri  redir_url  return  returnTo  returnto  return_url  returnUrl
returnToUrl  goto  dest  destination  target  target_url  continue
continueTo  continue_url  out  view  callback  to  forward  link  ref
referer  site  host  port  domain  path  location  uri  navigate  page
show  file  folder  dir  doc  document  download  load  feed  image  img
src  source  origin  back  prev  previous  root  home  start  entry
exit  leave  away  offsite  external  ext  outside  foreign  jump  hop
bridge  gateway  portal  via  through  via_url  RelayState  relay  ret
from  landing  ret_url  success  successUrl  cancel  cancelUrl  fail
failUrl  error  errorUrl  checkOutUrl  CheckoutUrl  checkout_url
logout  login  signin  signout  auth  oauth  sso  OnErrorContinue
load_uri  icon  banner  go  url_back  url_return  location_url  data
reference  end  ready  done  after  before  then  next_url  next_page
service  relay_state  ReturnUrl  ReturnTo  RequestedUrl  reply  resp
spoof  launch  content  auth_url  redirect_uri_encoded  redirectURL
```

## The context-anchored names — where each lives

| Context | The likely names |
|---|---|
| a login/logout/register flow | `next` `return` `returnTo` `goto` `continue` `back` `ret` |
| an OAuth/SSO/SAML flow | `redirect_uri` `callback` `RelayState` `relay` `return` `resp` `acs` `reply` |
| a link-shortener/outbound tracker | `url` `link` `target` `dest` `out` `u` `r` `l` |
| an image/asset/proxy fetcher | `image` `img` `src` `load` `feed` `uri` `file` `doc` |
| a payment/checkout flow | `successUrl` `cancelUrl` `failUrl` `errorUrl` `checkOutUrl` `return` |
| a tracking/affiliate redirect | `aff` `ref` `track` `campaign` `ad` `click` |
| a framework logout | `next` `next_page` `post_logout_redirect_uri` `return` |

## The OAuth/SSO-specific names — the high-value params

```text
redirect_uri     <- the OAuth callback — the allowlist-check is the surface
redirect         <- a shorter variant
post_logout_redirect_uri  <- OIDC logout — a redirect that leaks the session
RelayState       <- SAML — the post-auth destination
acs_url / assertion_consumer_url  <- the SAML ACS
reply / wreply   <- WS-Federation
return / resp    <- generic SSO returns
state            <- the OAuth state — a confusion with a redirect? (the state carries no host)
return_url       <- a generic
```

## The method-carrier matrix — GET vs POST vs Referer vs fragment

| Carrier | The param | The surface |
|---|---|---|
| a GET query | `?next=` | the common surface — the param in the URL |
| a POST body | `redirect=` | a form's hidden field — `?` no, a POST param |
| a Referer-derived | the Referer header | a `redirect back` that trusts the Referer — send a forged Referer |
| a fragment | `#next=` | a client-side read — `location.hash` flows into `location.href` |
| a cookie | a `return_url` cookie | a stored redirect — set the cookie, trigger the flow |
| a session field | a stored `next` | set once via a query, fires on the next login |

## The stored/persisted redirect — the two-step surface

```text
1. a param sets the return destination: /set-next?next=https://evil.com
   -> stored in a session/cookie
2. a later flow reads it: /login -> 302 to the stored next -> evil.com
```

A two-step redirect — the param is set on one endpoint, fired on another;
missed by a single-endpoint sweep.

## The back/reference redirect — the Referer trick

```text
/back /return /previous — a flow that 302s to the Referer
send: Referer: https://evil.com -> Location: https://evil.com
```

```bash
curl -si -H "Referer: https://evil.com" "$BASE/back" | grep -i '^location'
# Location: https://evil.com -> a Referer-derived open redirect
```

## The inventory-record

`param: <endpoint>: <the-param-name>: <the-carrier>: <the-context>` —
each candidate param + where it lives (query/body/Referer/cookie/session)
+ the flow context (login/oauth/tracker/fetcher).
