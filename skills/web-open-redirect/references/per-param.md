# Per-param — each redirect-param name and its context

## `next` / `continue` / `goto` / `to` / `forward` — the post-action landing

```text
context: a flow that lands somewhere after an action — login, logout,
         register, checkout, an upload-complete
check:   ?next=https://evil.com -> Location: ?
filter:  usually the most-filtered param; the //, %5c, userinfo arms
```

`next` is THE canonical param — `param-inventory.md` for the sweep. On a
login flow it lands post-auth; on logout it's the "where to after logout".

## `return` / `returnTo` / `return_url` / `ret` — the explicit return

```text
context: a return-after-action — payment returns, OAuth returns, a
         multi-step form's back-path
check:   ?return=https://evil.com / ?returnTo=...
filter:  often weaker than `next` — the "return" semantics imply a URL
```

## `url` / `link` / `target` / `dest` / `destination` — the named-URL

```text
context: a link-shortener, an outbound-click tracker, a "visit this" param,
         an image/feed/asset fetcher
check:   ?url=https://evil.com
filter:  often a fetcher — the URL may be fetched not redirected; if
         fetched it's SSRF not open-redirect; check the response type
```

## `redirect` / `redirect_uri` / `redirect_url` — the explicit redirect

```text
context: an OAuth/SSO flow's callback, a "redirect to" param, a form's
         post-submit destination
check:   ?redirect_uri=https://evil.com / ?redirect=...
filter:  redirect_uri on an OAuth flow is the highest-value — the
         allowlist-check on it is the OAuth surface; a gap launders the
         code to the canary (web-oauth-sso)
```

## `callback` / `relay` / `RelayState` / `reply` — the SSO returns

```text
context: SAML RelayState, WS-Federation wreply, an OAuth callback, an
         OIDC post_logout_redirect_uri
check:   ?RelayState=https://evil.com / ?callback=...
filter:  the SSO-flow returns — a gap here launders the SSO assertion
         or the logout to the canary
```

## `ref` / `referer` / `back` / `prev` / `previous` — the back-reference

```text
context: a "back" link, a Referer-derived return, a "previous page"
check:   ?back=https://evil.com, OR a Referer: header the server 302s to
filter:  the Referer-derived — forge the Referer header; the param-derived
         — the back param
```

## `view` / `page` / `show` / `out` / `link` — the view/destination

```text
context: a "view this page", a "go out to", an outbound view
check:   ?view=https://evil.com / ?out=...
filter:  lower-signal; often a page-loader not a redirect — read the
         response type
```

## `image` / `img` / `src` / `load` / `feed` / `uri` / `file` / `doc` — the fetcher

```text
context: an image-proxy, a feed-fetcher, a document-loader, a thumbnail
check:   ?img=https://evil.com/x.png / ?feed=...
filter:  a FETCHER — the response is the fetched CONTENT (SSRF surface)
         not a redirect; but a fetcher that follows Location reaches the
         redirect target (the open-redirect->SSRF chain)
```

## `success`/`cancel`/`fail`/`error`/`checkOutUrl` — the payment/checkout

```text
context: a payment-return URL, a checkout-cancel destination, a
         success/fail landing
check:   ?successUrl=https://evil.com / ?cancelUrl=...
filter:  the payment-return — a gap here lands the post-payment user on
         the canary
```

## `login`/`logout`/`signin`/`signout`/`auth`/`oauth`/`sso` — the auth-flow

```text
context: an auth-flow redirect — where to after login/logout/SSO
check:   ?post_logout_redirect_uri=https://evil.com (OIDC logout)
         ?next=https://evil.com (post-login)
filter:  the OIDC post_logout_redirect_uri is a named surface — it lands
         the user post-logout on the canary
```

## The param-to-chain matrix

| The param | The likely chain |
|---|---|
| `redirect_uri`/`callback`/`RelayState` | the OAuth/SSO code+token launder |
| `next`/`return`/`goto` | the post-auth phishing / a chain-hop |
| `url`/`img`/`feed`/`uri` | the fetcher->SSRF / a redirect-follow |
| `successUrl`/`cancelUrl` | the payment-flow launder |
| `back`/`prev`/Referer | the Referer-derived redirect |

## The per-param record

`param: <name>: <the-context>: <the-carrier>: <the-verdict>` — each
param's context + carrier + the measured Location verdict.
