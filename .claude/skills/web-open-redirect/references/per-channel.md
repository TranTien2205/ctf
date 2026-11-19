# Per-channel — each input channel the param arrives on

## Channel 1 — the GET query

```text
?next=<param>   <- the canonical — the param in the URL query
the carrier:    the GET request's query string
the arms:       every URL-bypass arm — the param is the URL-encoded value
```

```bash
curl -si "$BASE/login?next=https%3A%2F%2Fevil.com" | grep -i location
```

## Channel 2 — the POST body

```text
redirect=<param>  <- a form-carried param — application/x-www-form-urlencoded
the carrier:      the POST body — the param is a form field
the arms:         the same URL-bypass arms, sent as a body-param
```

```bash
curl -si -X POST "$BASE/login" -d 'user=a&pass=a&next=https%3A%2F%2Fevil.com' | grep -i location
```

## Channel 3 — the Referer header

```text
Referer: <param>   <- the header-carried — a /back that 302s to the Referer
the carrier:       the Referer header
the arms:          a forged Referer value
```

```bash
curl -si -H "Referer: https://evil.com" "$BASE/back" | grep -i location
```

## Channel 4 — the cookie

```text
Cookie: next=<param>  <- a stored cookie the flow reads
the carrier:          the cookie
the arms:             a set-cookie via a separate endpoint OR a forged cookie
```

```bash
curl -si -b "next=https://evil.com" "$BASE/login" | grep -i location
```

## Channel 5 — the session field

```text
session['next'] = <param>   <- a server-side session store
the carrier:                a param set on one endpoint, read on another
the arms:                   the two-step — /set-next?next=<canary> -> /login
```

```bash
curl -s -c c.txt "$BASE/set-next?next=https://evil.com"
curl -si -b c.txt "$BASE/login" | grep -i location
```

## Channel 6 — the fragment

```text
#next=<param>   <- the URL fragment — client-side only
the carrier:    the fragment — NEVER sent to the server; the page's JS reads it
the arms:       the fragment-carried JS-sink — ?#next=<canary> -> the JS reads
                location.hash -> location.href = <canary>
```

The fragment never reaches the server — a `#next=` param is invisible to a
server-side probe; the client-side JS reads it.

## Channel 7 — the localStorage/sessionStorage

```text
localStorage.next = <param>  <- a JS-side stored redirect
the carrier:                 a JS-set localStorage the page reads
the arms:                    the JS-sink — the param set via a separate
                             mechanism, the page reads it on a later nav
```

## Channel 8 — the path segment

```text
/redirect/<the-encoded-url>  <- a path-segment param
the carrier:                 the URL path
the arms:                    the path-encoded URL — /redirect/https%3A%2F%2Fevil.com
```

```bash
curl -si "$BASE/redirect/https%3A%2F%2Fevil.com" | grep -i location
```

## The channel-to-arm map

| The channel | The arm-encoding |
|---|---|
| GET query | `urllib.parse.quote` the arm |
| POST body | the form-encoded arm |
| Referer | the raw URL |
| cookie | the raw/arm |
| session | the GET-param on the set-endpoint |
| fragment | the JS-read raw |
| localStorage | the JS-set raw |
| path segment | the path-encoded arm |

## The per-channel record

`channel: <the-input-channel>: <the-carrier>: <the-arm>: <the-verdict>`
