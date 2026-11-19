# Theory — why open-redirect exists and why it's a class

## The trust-boundary model

```text
the server is a TRUSTED issuer — the client trusts where the server
sends it. a param that names the destination, unchecked, lets the
attacker borrow the server's trust: the client follows the server's
Location to the attacker's host.
```

The class is a TRUST-LAUNDERING primitive — the server's `Location:` is
the issuer of the destination; an unchecked param makes the server issue
the attacker's.

## Why the check is hard — the URL is not one string

```text
a URL is a structured object — scheme://userinfo@host:port/path?query#fragment
a filter that checks the STRING misses the PARSE; a filter that parses
with parser-A misses parser-B's read. The class is fundamentally a
parser-differential — the check reads one parse; the browser another.
```

## The allowlist fallacy — the filter shapes that fail

```text
1. the STRING check    — 'target.com' in url  -> substring arms
2. the PREFIX check    — startswith('/')       -> the // / \ arms
3. the SUFFIX check    — endswith('.target.com')-> the eviltarget.com gap
4. the PARSE check     — hostname==target.com   -> the userinfo/\@/encoded
5. the SCHEME check    — scheme in [http,https] -> the javascript:/data:
6. the DECODE check    — on the encoded string  -> the decode-order arms
```

Every filter shape fails on the arm it doesn't check — the class's
systematic surface.

## The laundered-trust model — why it matters

```text
the redirect alone:  a phishing link (low)
the redirect + trust: a code/token/fetch/bot/action laundered
  - OAuth:   the redirect_uri is trust-checked; an open-redirect on an
             allowlisted domain launders the code to evil.com
  - SSRF:    the fetcher trusts its allowlisted URL; a redirect the
             fetcher follows reaches the internal host
  - XSS:     the scheme-check misses a javascript:/data:
  - the bot: the bot trusts the target's URL; a redirect lands it on
             attacker content
```

## The client-side-vs-server-side model

```text
server-side:  the server's Location — the issuer is the server; the
              filter is the server's check
client-side:  the meta/JS — the issuer is the page's own code; the
              "filter" is the JS sanitization; the param reaches a
              DOM-sink
```

Same class, different carrier — the client-side twin bypasses the
server-side check entirely (the server never checked the destination;
the page's JS owns the nav).

## The two-parser model — the URL is not canonical

```text
urlparse('https://evil.com\\@target.com') -> hostname='evil.com'? or
                                            'target.com'? — the `\@` is
                                            a separator to some parsers
browser URL API -> host='target.com'      — the `\` is a path-sep
```

The URL RFC + WHATWG disagree on `\`, `\@`, `%5c`, `//`, the userinfo —
the disagreements ARE the bypass corpus.

## The class's place — the launder primitive

```text
open-redirect is a PRIMITIVE — a low-impact surface whose value is the
downstream trust. In a taxonomy it's the "redirect destination
uncontrolled" class; in a chain it's hop-1 to the laundered-trust flag.
```

## The theory-record

`theory: the-server-issues-the-destination -> the-param-controls-it ->
the-filter-misses-one-parse -> the-client-follows-to-the-attacker` —
the trust-laundering mechanism.
