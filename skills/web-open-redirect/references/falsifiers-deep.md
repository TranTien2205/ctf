# Falsifiers (deep) — the complete class-closing observations

## The class-falsifier — the precise statement

```text
the destination is validated against an allowlist or forced to a
relative path — measured by a Location: <safe> on EVERY canary + bypass
arm; the arms-tried list + the verbatim safe Locations are the falsifier's
evidence
```

## The falsifier decision-table

| The observation | The falsifier it proves | The reopen |
|---|---|---|
| `Location: /` on all canaries + bypasses | the allowlist/relative-force holds | a different endpoint / a stored-redirect / a Referer-derived surface |
| `Location: <allowlisted>` on all arms | the host-allowlist holds | an open-redirect ON an allowlisted domain (the chain-hop) |
| a `400`/`422` on every param | the param validation rejects the format | a different param name / a different carrier |
| the meta-refresh value is escaped | the client-side twin is sanitized | a different sink / a DOM-source the sanitizer misses |
| the `location.href` value is escaped | the JS sanitizes | a different sink |
| the `javascript:` is rejected | the scheme-check holds | a `data:`/`blob:`/`vbscript:` alternative |
| the `//` is normalized to `/` | the `//`-block holds | the `/\`/`\\`/`%5c`/`%2f` arms |
| the `@` is normalized | the userinfo is rejected | the `\@`/encoded-`@`/query-`@` arms |
| the Referer is checked | the Referer-derived is closed | — |
| the stored value re-validated | the stored-redirect is closed | — |

## The mechanism-level falsifiers — per surface

### the post-login `next` falsifier

```text
?next=<every arm> -> Location: /dashboard  <- the login-redirect is
                                             allowlisted -> this SURFACE
                                             is closed; check /logout,
                                             /error, the Referer-derived
```

### the OAuth `redirect_uri` falsifier

```text
?redirect_uri=<every arm> -> an error / a rejected redirect_uri
                           -> the allowlist is strict AND no allowlisted
                              domain has an open-redirect -> the CHAIN is
                              closed for that allowlist
```

### the fetcher-follow falsifier

```text
/fetch?url=<a-redirect-chain> -> the fetcher returns the redirect-page's
                                 content (NOT the internal host) -> the
                                 fetcher doesn't follow -> the SSRF-chain
                                 is dead
```

### the `javascript:`/`data:` falsifier

```text
?url=javascript:... -> Location: /  OR  the scheme normalized to http
?url=data:...       -> Location: /  OR  rejected
                     -> the scheme-check holds -> the XSS-twin is closed
```

### the client-side-twin falsifier

```text
?url=<param> -> <meta content="0;url=/safe">     <- the meta sanitizes
?url=<param> -> location.href=escape(url)         <- the JS sanitizes
?url=<param> -> the param isn't read by the JS    <- a different sink
```

### the stored-redirect falsifier

```text
/set-next?next=evil.com -> stored
/login -> Location: /    <- the stored re-validated at read-time
```

### the Referer-derived falsifier

```text
GET /back  Referer: https://evil.com -> Location: /default
                                     <- the Referer isn't read / checked
```

## The uniform-falsifier — the class-closing observation

```text
the canary + EVERY bypass arm -> Location: <the-same-safe>
  ?next=https://evil.com           -> Location: /
  ?next=//evil.com                 -> Location: /
  ?next=/\evil.com                 -> Location: /
  ?next=%5cevil.com                -> Location: /
  ?next=https://target.com@evil.com -> Location: /
  ?next=evil.com\@target.com       -> Location: /
  ?next=https://target.com.evil.com -> Location: /
  ?next=javascript:alert(1)        -> Location: /
  ?next=%252f%252fevil.com         -> Location: /
```

A uniform `Location: <safe>` across every arm = the class's mechanism-level
falsifier — the validation holds regardless of the parse boundary.

## The "closed-but-reopen" falsifier — the surface-shift

```text
the class falsifier fires on /login — BUT:
  - a DIFFERENT endpoint hasn't been swept -> /logout, /error, /out, /goto
  - a DIFFERENT carrier hasn't been swept  -> the Referer-derived, the stored
  - a DIFFERENT param name hasn't been swept -> the vocabulary
the falsifier closes THE SWEPT SURFACE — reopen on a new surface
```

## The kill-map entry — the full falsifier record

```json
{
  "challenge": "<name>", "class": "web-open-redirect", "verdict": "closed",
  "surface": "/login?next=",
  "arms_tried": [
    "https://evil.com", "//evil.com", "/\\evil.com", "\\\\evil.com",
    "/%5cevil.com", "%5c%5cevil.com", "https://target.com@evil.com",
    "evil.com\\@target.com", "https://target.com.evil.com",
    "https://evil.com/target.com", "https%3a%2f%2fevil.com",
    "https%253a%252f%252fevil.com", "javascript:alert(1)",
    "data:text/html,<script>", "https:evil.com"
  ],
  "uniform_response": "Location: / on all arms",
  "falsifier": "the destination is validated against an allowlist or forced to a relative path",
  "reopen_precondition": "an unswept endpoint (logout/error/out/goto), a stored-redirect, a Referer-derived surface, a different param name"
}
```

## The falsifier-record command

```bash
python3 tools/hooks.py post-probe <challenge> --hypothesis-id <id> \
  --class web-open-redirect --verdict falsifies \
  --evidence 'Location: / on canary + // + %5c + @ + subdomain + javascript:' \
  --response '<the verbatim safe Locations>'
```
