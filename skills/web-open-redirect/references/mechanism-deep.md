# Mechanism (deep) — the complete trust-laundering model

## The full architecture

```text
[the client]                                        [the attacker]
     |                                                    |
     | GET https://target.com/login?next=<X>              | controls X
     v                                                    |
[target.com]                                              |
  - reads next=X                                          |
  - (maybe) validates X against a filter                  |
  - emits 302 Location:<the-resolution-of-X>              |
     |                                                    |
     v                                                    |
[the client's browser]                                    |
  - resolves the Location with the WHATWG URL parser      |
  - navigates to the resolved URL                         |
     |                                                    |
     +-----------------> https://attacker.invalid <-------+
                          the laundered destination
```

## The five components — where each is attackable

```text
1. the param       <- the input surface — which name, which carrier
2. the filter      <- the server's check — the parse-boundary it reads
3. the resolution  <- how the param becomes the Location — the decode
4. the carrier     <- the Location:/meta/JS — where the destination lands
5. the navigation  <- the browser's parse — the WHATWG resolution
```

## Component 1 — the param (the input surface)

```text
the GET query      ?next=X          <- the common surface
the POST body      redirect=X       <- a form-carried param
the Referer header Referer: X       <- a header-carried param
the cookie         next=X           <- a stored-carried param
the fragment       #next=X          <- a fragment-carried (client-side)
the session        session['next']  <- a stored server-side
```

The param's CARRIER determines how it reaches the redirect — a GET query
is the common surface; the Referer/cookie/session are the stored/header
variants; the fragment is client-side only.

## Component 2 — the filter (the server's check)

```text
the no-check       redirect(next)            -> any URL passes
the prefix-check   next.startswith('/')      -> the // / \ arms
the contains-check 'target.com' in next      -> the substring arms
the suffix-check   next.endswith('target.com') -> the no-boundary arm
the parse-check    urlparse(next).hostname in allowed -> the parser arms
the scheme-check   urlparse(next).scheme in [http,https] -> the scheme arms
the decode-check   on the raw/encoded/decoded form      -> the decode arms
```

The filter's SHAPE names which arm defeats it — the fingerprint is the
one `Location:` that survives the first canary.

## Component 3 — the resolution (how the param becomes the Location)

```text
the verbatim pass      redirect(next)         -> Location: <the-param>
the decode-then-pass   redirect(unquote(next)) -> Location: <decoded>
the join               redirect(urljoin(base, next)) -> Location: <resolved>
the template           redirect(f"{base}{next}") -> Location: <interpolated>
the conditional        redirect(next if valid else '/') -> Location: <the-branch>
```

The resolution determines what the param looks like in the `Location:` —
verbatim, decoded, joined, templated, or gated through a branch.

## Component 4 — the carrier (where the destination lands)

```text
Location: header   <- the 3xx response header — the canonical carrier
Refresh: header    <- a non-Location header — Refresh: 0;url=X
meta refresh       <- <meta content="0;url=X"> — a client-side carrier
JS navigation      <- location.href=X — a client-side carrier
location.hash      <- a fragment-nav — same-page unless re-read
```

The carrier is where the evidence lives — the verbatim `Location:` value
for the server-side; the `content=`/`location.href=` value for the client.

## Component 5 — the navigation (the browser's parse)

```text
the browser resolves the Location with the WHATWG URL parser:
  Location: //evil.com       -> https://evil.com   (scheme-relative)
  Location: /\evil.com       -> https://evil.com   (the \ -> /)
  Location: \\evil.com       -> https://evil.com   (the \\ -> //)
  Location: https://a@evil.com -> https://evil.com (the @ userinfo)
  Location: evil.com         -> https://target.com/evil.com (relative)
  Location: https:evil.com   -> https://target.com/evil.com? or https://evil.com? (WHATWG splits)
```

The browser's parse is what makes the differential arms fire — the server
checked one parse; the browser resolves another.

## The differential model — the core mechanism

```text
the filter reads:      urlparse(X) / URI.parse(X) / a regex / a string-op
the browser resolves:  WHATWG URL — the living standard
the bypass:            an X where filter-parse(X).host ≠ browser-parse(X).host
```

The WHATWG parser's quirks — `\`→`/`, `\\`→`//`, `\@`, `%5c`, the
scheme-less `//`, the userinfo `@`, the fullwidth chars — are the
differential corpus.

## The trust-flow — the launder

```text
the trust flows:  client trusts target.com -> target.com issues Location
                  -> client follows Location -> lands on attacker host
the trust is BORROWED — the client's trust in target.com is used to send
it to the attacker's host
```

## The chain-mechanism — the laundered-trust flow

```text
the OAuth flow:    the OAuth server trusts the allowlisted redirect_uri;
                   the open-redirect ON that allowlisted domain launders
                   the code to the attacker
the SSRF flow:     the fetcher trusts its allowlisted URL; the redirect
                   the fetcher follows reaches the internal host
the XSS flow:      the sink trusts the param's scheme; a javascript:/
                   data: reaches the sink
the phishing flow: the victim trusts the target.com URL; the redirect
                   lands them on the attacker's domain
```

## The mechanism-graph

```text
param -> filter -> resolution -> carrier -> navigation -> destination
  |        |          |           |           |              |
  |        |          |           |           |              + the launder
  |        |          |           |           + the WHATWG parse
  |        |          |           + Location/meta/JS/Refresh
  |        |          + verbatim/decode/join/template
  |        + the check's parse
  + the input surface
```

Each node is attackable; the corpus maps each node's arms.
