# Mechanism catalogue — every mechanism, catalogued

## The redirect mechanisms — the carrier catalogue

```text
SERVER-SIDE:
  1. the 302 Found + Location      <- the common — the method drops on the follow
  2. the 301 Moved Permanently     <- the permanent — may be CACHED
  3. the 303 See Other             <- the REST-shape — always re-GETs
  4. the 307 Temporary Redirect    <- keeps the method + body
  5. the 308 Permanent Redirect    <- keeps the method + body — may be cached
  6. the Refresh: header           <- a non-Location response header
CLIENT-SIDE:
  7. the <meta http-equiv=refresh> <- the tag — content="0;url=X"
  8. window.location = X           <- the global assignment
  9. location.href = X             <- the property
  10. location.replace(X)          <- the method — no history entry
  11. location.assign(X)           <- the method — a history entry
  12. location = X                 <- the bare assignment
  13. location.hash = X            <- a fragment-nav — same-page unless re-read
  14. history.pushState(..., X)    <- a same-origin path-change
  15. history.replaceState(..., X) <- a same-origin path-change
  16. document.location = X        <- the document variant
  17. self.location = X            <- the self variant
  18. top.location = X             <- the top-frame variant
  19. window.open(X)               <- a new-window nav
  20. a fetch-API redirect         <- a JS-carried nav
```

## The param mechanisms — the input catalogue

```text
1. the GET query param            ?next=X
2. the POST body param            redirect=X (form-encoded)
3. the Referer header             Referer: X
4. the cookie param               Cookie: next=X
5. the session field              session['next']=X
6. the fragment param             #next=X (client-side only)
7. the localStorage               localStorage.next=X
8. the sessionStorage             sessionStorage.next=X
9. the path-segment               /redirect/<X>
10. the hidden form field         <input name=redirect value=X>
```

## The filter mechanisms — the check catalogue

```text
1. the no-check                    -> any URL passes
2. the startswith('/')             -> the // and \ arms
3. the startswith('/') && !//      -> the /\ and %5c arms
4. the contains('target.com')      -> the substring arms
5. the endswith('target.com')      -> the no-boundary arm
6. the hostname== / netloc==       -> the userinfo/\@/encoded arms
7. the host-in-allowlist           -> the parser-differential arms
8. the scheme-check                -> the javascript:/data:/scheme arms
9. the regex-check                 -> the regex-boundary arms
10. the decode-order check         -> the encoded/double arms
11. the unicode/ASCII check        -> the fullwidth arms
12. the whitespace/trim check      -> the whitespace/control arms
13. the framework-check            -> the framework-matrix arms
14. the signature/nonce check      -> a closed surface
```

## The chain mechanisms — the launder catalogue

```text
1. the OAuth redirect_uri launder  -> the code/token on the canary
2. the OIDC post_logout launder    -> the logout redirect
3. the SAML RelayState launder     -> the SSO post-auth redirect
4. the SSRF-fetch-follow           -> the internal host
5. the XSS-scheme-sink             -> the javascript:/data: fire
6. the bot-visit launder           -> the bot's session/content
7. the phishing launder            -> the domain-reputation borrow
8. the CRLF-split                  -> the header-injection twin
9. the Referer-leak                -> the originating URL's token
10. the token-in-fragment launder  -> the OAuth implicit's #access_token
11. the cookie-scope launder       -> the *.evil.com cookies
12. the cached-redirect            -> the CDN/proxy's stored redirect
13. the deep-link launder          -> the QR/app-link
```

## The catalogue-record

`catalogue: <the-mechanism-family>: <the-mechanism> -> <the-arm>`
