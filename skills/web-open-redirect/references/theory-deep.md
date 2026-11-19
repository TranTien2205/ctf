# Theory (deep) — the trust-laundering model in full

## The redirect as a capability

```text
the server's Location: header is a CAPABILITY — it orders the client to
navigate. A param controlling that capability unchecked is a confused-
deputy primitive: the server's authority executes the attacker's order.
```

## The URL-is-not-a-string principle

```text
a URL is a structured object — scheme://userinfo@host:port/path?query#frag
a STRING-check reads bytes; a PARSE-check reads a structured field.
every open-redirect bypass is the gap between the check's read and the
browser's WHATWG resolve — the URL parses differently for each.
```

## The WHATWG-URL-vs-RFC-3986 differential

```text
RFC-3986 (urlparse, most server parsers):
  - strict scheme:path //authority/path
  - the '\' is an invalid char — most RFC parsers treat it as a path-char
  - the userinfo@host split is on the LAST @
WHATWG (the browser's URL living standard):
  - '\' is a path-separator — same as '/'
  - 'https://evil.com\@target.com' -> the '\' makes evil.com a path-seg;
    the host is 'target.com'
  - '//' is scheme-relative — inherits the base scheme
  - 'https:evil.com' -> an absolute-scheme URL — host='evil.com'
```

The differential IS the bypass corpus — the server checks RFC-3986, the
browser resolves WHATWG.

## The trust-laundering principle

```text
the redirect's VALUE is the trust it carries:
  - the OAuth server trusts the allowlisted redirect_uri -> the open-
    redirect ON that domain launders the code
  - the fetcher trusts its allowlisted URL -> the redirect it follows
    launders the internal host
  - the victim trusts the target.com link -> the redirect launders the
    phishing domain
  - the bot trusts the target's URL -> the redirect launders the bot's
    session onto attacker content
```

## The catalogue-vs-verified principle

```text
the class is CATALOGUE — the corpus is the PUBLISHED bypass-alphabet,
not a locally-measured chain. a verbatim Location: <canary> on a live
target is the local confirm — until one lands, the class is standard
knowledge an agent applies, not experience it inherits.
```

## The theory-record

`theory: the-Location-is-a-capability -> the-param-controls-it ->
the-parser-differential-is-the-bypass -> the-laundered-trust-is-the-value`
