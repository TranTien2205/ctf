# Detection signals — every observable that says "redirect surface here"

## The param-name signals

```text
the STRONG names (high-signal — almost always a redirect):
  next, redirect, redirect_uri, redirect_url, returnTo, returnto,
  return_url, post_logout_redirect_uri, RelayState, relay, callback
the MEDIUM names (context-dependent):
  url, redir, return, goto, dest, destination, target, continue, out,
  view, to, forward, link, ref, back, prev, previous
the WEAK names (low-signal — check context):
  ret, from, site, host, path, location, uri, navigate, page, show,
  landing, image, img, src, feed, file, doc, load, uri, success, cancel
```

## The endpoint-name signals

```text
the STRONG endpoints:
  /login /signin /logout /signout /auth/* /oauth/* /sso /saml/* /oidc/*
  /out /goto /redirect /return /link /r /u
the MEDIUM endpoints:
  /error /401 /403 /404 /checkout /payment/* /register /wizard /form
the LOWER endpoints:
  /img /fetch /proxy /thumb /feed /share /qr /deeplink
```

## The response signals

```text
a 3xx status            <- a redirect happens — surface
a Location: header      <- the carrier — surface
a Refresh: header       <- a header carrier — surface
a <meta refresh>        <- the client-side twin — surface
a location.* in the JS  <- the client-side twin — surface
a Location: <the-param> <- the param reaches the Location — CANDIDATE-surface
```

## The bundle/JS signals

```text
location.href = ...        <- a JS nav-sink
location.replace(...)      <- a JS nav-sink
location.assign(...)       <- a JS nav-sink
window.location = ...      <- a JS nav-sink
location.hash = ...        <- a fragment-nav
new URLSearchParams(location.search).get('next')  <- the param-read source
localStorage.next / sessionStorage.next            <- a stored-redirect source
history.pushState(...)     <- a same-origin path-change
document.referrer          <- a Referer-read
```

## The filter-shape signals — the Location fingerprint

```text
Location: <canary>           <- no filter / a broken check — CANDIDATE
Location: /                  <- a forced-relative filter
Location: <allowlisted-host> <- a host-allowlist filter
Location: <partial>          <- a path/host-force filter
Location: <the-param> relative <- a relative-resolution — a negative
Location: <javascript:>      <- a scheme-pass — a candidate
no Location                  <- a weak-negative — not a redirect param
```

## The chain signals

```text
an OAuth/SSO flow present         -> the redirect_uri launder surface
a fetcher present                 -> the SSRF-fetch-follow surface
a client-side sink present        -> the javascript:/data: surface
a bot/report-URL feature          -> the bot-visit surface
a phishing-shaped challenge       -> the standalone launder surface
a %0d%0a reaching the header      -> the CRLF-split surface
```

## The falsifier signals

```text
Location: <safe> on EVERY canary + arm  -> the class falsifier
no Location on every param              -> the vocabulary is wrong
the meta/JS escaped                     -> the client-side twin closed
the scheme rejected                     -> the scheme-surface closed
```

## The signal-confidence map

| The signal | The confidence |
|---|---|
| the param name | low — a name-match |
| a Location exists | low — the redirect exists |
| `Location: <canary>` | high — the oracle |
| `Location: <safe>` on all arms | high — the falsifier |
| the meta/JS carries the param | medium — the client-side twin |
| the laundered-trust fires | highest — the impact |

## The signal-record

`signal: <the-observable>: <the-confidence>: <the-next-probe>`
