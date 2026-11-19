# Per-surface — each endpoint/flow that carries a redirect param

## Surface 1 — the post-login landing

```text
/login?next=...   /signin?next=...   /auth/login?return=...
the flow: auth succeeds -> 302 to `next` -> the post-auth landing
the surface: the most-common + most-filtered; the error-path variant
             (/login?next=... on a FAILED login) is often less-filtered
```

## Surface 2 — the post-logout landing

```text
/logout?next=...   /logout?post_logout_redirect_uri=...
the flow: logout -> 302 to `next`/`post_logout_redirect_uri`
the surface: an OIDC `post_logout_redirect_uri` is a named surface —
             often registered/allowlisted per-client but a gap launders
             the post-logout destination
```

## Surface 3 — the OAuth/SSO callback

```text
/oauth/authorize?redirect_uri=...   /sso/callback?relay=...
/saml/acs?RelayState=...   /oidc/callback?...
the flow: the SSO return — the highest-value; a redirect_uri allowlist
          gap launders the code/token to the canary (web-oauth-sso)
```

## Surface 4 — the link-shortener / outbound-click tracker

```text
/out?url=...   /goto?url=...   /link?target=...   /r?u=...
the flow: a click-tracker that 302s to the destination
the surface: often unfiltered (the feature IS a redirect); the param
             names url/target/dest/u/link — a strong open-redirect surface
```

## Surface 5 — the image/asset/feed fetcher

```text
/img?url=...   /proxy?url=...   /fetch?uri=...   /thumb?src=...
the flow: a server-side fetch — the SSRF twin; the fetcher may follow
          redirects -> a redirect on the fetched URL reaches internal
the surface: check if the response is fetched-CONTENT (SSRF) vs a
             redirect (open-redirect)
```

## Surface 6 — the multi-step form's back/return

```text
/wizard?back=...   /form/step2?return=...   /checkout?cancel=...
the flow: a multi-step flow's back-path
the surface: the "return to step" / "cancel" destination — often a
             weaker check than the main `next`
```

## Surface 7 — the error-path redirect

```text
/error?next=...   /401?return=...   /403?next=...   /404?url=...
the flow: an error -> redirect to a "next"/"return"
the surface: the error-path is the most-missed — the redirect after a
             failed auth/error often honours `next` with a weaker check
```

## Surface 8 — the stored-redirect (the two-step)

```text
/set-next?next=...  +  /login -> fires the stored next
the flow: a param persists the destination; a later flow fires it
the surface: a single-endpoint sweep misses it — `stored-and-referer.md`
```

## Surface 9 — the Referer-derived

```text
/back   /return   /previous   — reads the Referer header
the flow: the server 302s to the Referer
the surface: forge the Referer header — `Referer: https://evil.com`
```

## Surface 10 — the client-side bundle-sink

```text
the bundle's JS: location.href = getParam('next')
the flow: a client-side redirect — no server Location; the param is
          read by the page's JS
the surface: `client-side.md` — a DOM-source sink; check the bundle
```

## Surface 11 — the meta-refresh

```text
the response: <meta http-equiv="refresh" content="0;url=<param>">
the flow: a server-rendered meta-refresh — the param in the content attr
the surface: `client-side.md`
```

## Surface 12 — the QR/barcode/deep-link generator

```text
/qr?url=...   /deeplink?target=...   /share?link=...
the flow: a QR-code / deep-link / share-link generator embedding the URL
the surface: the generated URL is scanned/opened — a laundered link
```

## The surface-to-param map

| The surface | The param names |
|---|---|
| post-login | `next` `return` `goto` `continue` `to` |
| post-logout | `next` `post_logout_redirect_uri` `return` |
| OAuth/SSO | `redirect_uri` `callback` `RelayState` `relay` `reply` |
| tracker | `url` `link` `target` `dest` `u` `out` |
| fetcher | `url` `img` `src` `uri` `feed` `file` |
| multi-step | `back` `return` `cancel` `prev` |
| error-path | `next` `return` `url` `ref` |
| Referer | (the Referer header) |
| QR/deep-link | `url` `link` `target` `data` |
