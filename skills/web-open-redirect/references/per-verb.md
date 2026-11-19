# Per-verb — the HTTP method each redirect surface accepts

## GET — the query-carried param

```text
GET /login?next=<param>          <- the canonical — the param in the URL
the carrier:                     the query string
the arms:                        the URL-bypass corpus, URL-encoded
the evidence:                    the verbatim Location: header
```

```bash
curl -si "$BASE/login?next=https%3A%2F%2Fevil.com" | grep -i location
```

## POST — the body-carried param

```text
POST /login  redirect=<param>    <- a form-carried param
the carrier:                     the request body — application/x-www-form-urlencoded
the arms:                        the same corpus, form-encoded
the 302-behavior:                a 302 on a POST -> the client re-issues a GET
                                 (the method drops); a 307 keeps the POST
```

```bash
curl -si -X POST "$BASE/login" -d 'user=a&pass=a&next=https%3A%2F%2Fevil.com' | grep -i location
```

## POST + JSON — the API-carried param

```text
POST /api/login  {"next": "<param>"}   <- a JSON-carried param
the carrier:                          the JSON body
the arms:                             the URL-bypass corpus as a JSON string
the response:                         a JSON body OR a redirect — check both
```

```bash
curl -si -X POST "$BASE/api/login" -H 'Content-Type: application/json' \
  -d '{"next":"https://evil.com"}' | grep -i location
```

## The method-switch — the GET/POST differential

```text
some surfaces accept BOTH GET and POST — the param's carrier changes the
encoding but not the URL-bypass corpus
some surfaces are POST-only — the GET param is ignored — the POST carries it
```

```bash
# the GET variant
curl -si "$BASE/login?next=//evil.com" | grep -i location
# the POST variant
curl -si -X POST "$BASE/login" -d 'next=//evil.com' | grep -i location
```

## The redirect-status × method matrix

```text
302 on GET   -> the follow is a GET — the common redirect
302 on POST  -> the follow is a GET — the method drops
303 on POST  -> the follow is a GET — always
307 on POST  -> the follow is a POST — the method + body keep
308 on POST  -> the follow is a POST — the method + body keep
```

For the open-redirect surface the method is surface-detail — the `Location:`
carries the canary regardless; but for a POST-carried redirect the 307/308
keeps the POST to the canary — a CSRF-redirect twin.

## The fragment — the non-verb channel

```text
#next=<param>   <- the fragment is NEVER sent — a client-side-only channel
the surface:    the page's JS reads location.hash -> location.href
```

## The header — the non-body channel

```text
Referer: <param>   <- a header-carried — a /back that 302s to the Referer
X-Forwarded-Host   <- a trust-header — the host-header twin (web-host-header)
```

## The verb-to-carrier map

| The verb/channel | The carrier | The encoding |
|---|---|---|
| GET | the query | `urllib.parse.quote` |
| POST form | the body | `urllib.parse.quote` |
| POST JSON | the JSON string | the raw URL in the JSON |
| the Referer | the header | the raw URL |
| the cookie | the cookie | the raw URL |
| the fragment | the `#` | the raw (JS reads it) |
| the localStorage | the JS | the raw (JS reads it) |
| a path segment | the URL path | `quote(arm, safe='')` |

## The per-verb record

`verb: <the-method/channel>: <the-carrier>: <the-arm>: <the-verdict>`
