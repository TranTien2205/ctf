# Per-mechanism — each mechanism's deep treatment

## Mechanism — the server-side `Location:` redirect

```text
the mechanism: the server emits a 3xx + Location: <the-param-resolution>
the attack:    the param is unchecked -> the Location carries the canary
the arms:      the //, /\, \\, %5c, %2f, @, \@, subdomain, substring,
               scheme, encoded, double-encoded, unicode, whitespace arms
the evidence:  the verbatim Location: header
```

## Mechanism — the client-side meta-refresh

```text
the mechanism: a server-rendered <meta http-equiv="refresh" content="0;url=X">
the attack:    the param lands in the content attribute unchecked
the arms:      the same URL-bypass arms + the scheme-arms (javascript:/data:)
the evidence:  the verbatim content="0;url=<canary>"
```

## Mechanism — the client-side JS-navigation

```text
the mechanism: the page's JS reads a param and assigns it to location.*
the attack:    a DOM-source sink — the param reaches location.href unchecked
the arms:      the URL-bypass + the scheme + the fragment-carried
the evidence:  the verbatim location.href="<canary>" assignment
```

## Mechanism — the `location.hash` fragment-carried

```text
the mechanism: the fragment #next=<param> is read by the page's JS
the attack:    the fragment never reaches the server — a client-side-only
               param the JS parses into location.href
the evidence:  the JS's location.href assignment after the hash-parse
```

## Mechanism — the stored-redirect (the two-step)

```text
the mechanism: a param persists (session/cookie/field), fires on a later flow
the attack:    /set-next?next=<canary> -> /login fires the stored -> canary
the arms:      the same URL-bypass arms, on the SET-step
the evidence:  the verbatim Location: on the FIRE-step
```

## Mechanism — the Referer-derived

```text
the mechanism: the server 302s to the Referer header
the attack:    Referer: <canary> -> Location: <canary>
the evidence:  the verbatim Location: carrying the forged Referer
```

## Mechanism — the `Refresh:` header

```text
the mechanism: a non-Location Refresh: response header — Refresh: 0;url=X
the attack:    the param lands in the Refresh header's url=
the evidence:  the verbatim 'Refresh: 0;url=<canary>'
```

## Mechanism — the CRLF-split

```text
the mechanism: a %0d%0a in the param reaching the Location: header bytes
the attack:    the CRLF splits the Location into a second header
the evidence:  the verbatim split headers — 'Location: /\r\nSet-Cookie: x=y'
```

## The per-mechanism verdict-table

| The mechanism | The oracle | The falsifier |
|---|---|---|
| the `Location:` | `Location: <canary>` | `Location: <safe>` on all arms |
| the meta-refresh | `content="0;url=<canary>"` | the `content` sanitized |
| the JS-nav | `location.href="<canary>"` | the value escaped |
| the `location.hash` | the hash-parse + the nav | the param isn't hash-read |
| the stored-redirect | the `Location:` on the fire | the stored re-validated |
| the Referer-derived | `Location: <the-Referer>` | the Referer checked |
| the `Refresh:` | `Refresh: 0;url=<canary>` | the `url=` sanitized |
| the CRLF | the split headers | `%0d%0a` stripped |

## The mechanism-record

`mechanism: <the-carrier>: <the-arm>: <the-oracle>: <the-verdict>`
