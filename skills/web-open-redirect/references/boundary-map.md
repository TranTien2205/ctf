# Boundary map — the parse-boundary → the arm → the verdict navigation

## The boundary-family map

```text
the SLASH boundary:
  / vs //    -> the scheme-relative gap
  / vs \     -> the backslash normalize gap
  / vs %2f   -> the encoded-slash gap
  // vs /\   -> the mixed-separator gap
the AT boundary:
  @          -> the userinfo split
  \@         -> the backslash-@ differential
  %40        -> the encoded-@
  ?@ #@      -> the query/fragment-@
the DOT boundary:
  .          -> the suffix/subdomain boundary
  %2e        -> the encoded-dot
  the trailing-dot target.com.  -> the DNS-normalize gap
the SCHEME boundary:
  http/https -> the allowed-schemes
  javascript:/data:/file:/...   -> the non-http schemes
  a scheme with no //            -> the scheme-relative-gap
the DECODE boundary:
  %XX        -> the single-decode
  %25XX      -> the double-decode
  the raw vs the decoded          -> the decode-order
the UNICODE boundary:
  %ef%bc%8f = ／  %ef%bc%a0 = ＠   -> the fullwidth
  %e3%80%82 = 。                  -> the ideographic
the WHITESPACE boundary:
  %20 %09 %0a %0d                 -> the whitespace/control
the AUTHORITY boundary:
  userinfo@host:port              -> the netloc-vs-hostname gap
  the port :443 :0 :65535         -> the port-edge
```

## The boundary → the arms map

| The boundary | The arms |
|---|---|
| `startswith('/')` | `//evil.com`, `/\evil.com`, `/\/evil.com`, `/%5cevil.com`, `/%2fevil.com` |
| `startswith('/') && !//` | `/\evil.com`, `/%5cevil.com`, `/\/evil.com`, `/%2fevil.com` |
| `\\` | `\\evil.com`, `\\%5cevil.com` |
| `\@` | `evil.com\@target.com`, `evil.com%5c@target.com`, `evil.com%5c%40target.com` |
| the userinfo `@` | `target.com@evil.com`, `target.com:443@evil.com`, `user:pass@evil.com` |
| the query-`@` | `evil.com?@target.com`, `evil.com%3f%40target.com` |
| the fragment-`@` | `evil.com#@target.com`, `evil.com%23%40target.com` |
| the suffix `.` | `target.com.evil.com`, `x.target.com.evil.com`, `target-com.evil.com` |
| the no-boundary | `eviltarget.com` |
| the substring-in-path | `evil.com/target.com`, `evil.com/x/target.com` |
| the substring-in-query | `evil.com?target.com`, `evil.com?x=target.com` |
| the substring-in-fragment | `evil.com#target.com` |
| the encoded-dot | `target.com%2eevil.com`, `target.com%252eevil.com` |
| the trailing-dot | `target.com.`, `target.com..` |
| the scheme-no-// | `https:evil.com`, `https:/evil.com`, `https:/\evil.com`, `https:\\evil.com` |
| the javascript-scheme | `javascript:alert(1)`, `javascript://%0aalert(1)` |
| the data-scheme | `data:text/html,<script>`, `data:...;base64,...` |
| the other-schemes | `file:///x`, `vbscript:`, `intent://`, `about:blank`, `jar:` |
| the encoded-// | `%2f%2fevil.com`, `https:%2f%2fevil.com` |
| the encoded-full | `https%3a%2f%2fevil.com` |
| the double-encoded | `https%253a%252f%252fevil.com`, `%255cevil.com` |
| the fullwidth | `https:%ef%bc%8f%ef%bc%8fevil.com`, `evil%ef%bc%8ecom`, `evil%ef%bc%a0target.com` |
| the ideographic | `evil%E3%80%82com` |
| the whitespace | `%20https://evil.com`, `%09https://evil.com`, `https://evil.com%20` |
| the control | `%0ahttps://evil.com`, `%0d%0ahttps://evil.com`, `https://evil.com%0d%0aSet-Cookie:x` |
| the port | `evil.com:443`, `evil.com:0`, `evil.com:65535` |
| the IPv6 | `[::ffff:127.0.0.1]`, `[::1]` |
| the multiple-@ | `a@b@c@evil.com`, `a:b@c@evil.com` |

## The boundary → the verdict map

```text
the arm -> the verbatim Location -> the verdict:
  a Location: <canary>      -> CANDIDATE — the boundary's gap fired
  a Location: <safe>        -> the boundary holds — the next arm
  a Location: <partial>     -> a different boundary — the fingerprint
```

## The boundary-record

`boundary: <the-parse-boundary>: <the-arms>: <the-verdict>`
