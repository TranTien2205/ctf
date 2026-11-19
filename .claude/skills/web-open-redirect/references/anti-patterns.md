# Anti-patterns — the approaches that don't work on open-redirect

## Anti-pattern 1 — the blind payload-list sweep

```text
the failure: sweeping EVERY bypass arm on EVERY param without reading the
             Location fingerprint — 100 arms × 20 params = 2000 requests
             and no filter-shape read
the fix:     send ONE canary, read the ONE Location — the fingerprint names
             which arm family to try; the blind sweep wastes the budget
```

## Anti-pattern 2 — "the param exists so it's a redirect"

```text
the failure: a param NAMED `next`/`url`/`redirect` that isn't a redirect
             param — a `200 render`, a `400`, a `Location:` to a fixed page
the fix:     the verbatim `Location:` is the oracle — the param NAME is a
             hint, not a surface
```

## Anti-pattern 3 — the `-L` follow

```text
curl -sL "$BASE/login?next=https://evil.com"
the failure: -L follows the redirect — you never see the Location header
the fix:     -si + grep -i '^location' — the verbatim header is the evidence
```

## Anti-pattern 4 — claiming the chain without the launder

```text
the failure: "the open-redirect lets me steal the OAuth code" — without
             actually confirming the open-redirect is on an allowlisted
             redirect_uri domain AND the code lands on the canary
the fix:     the chain needs each hop's verbatim evidence — the Location
             on hop-1, the redirect_uri on hop-2, the code on hop-3
```

## Anti-pattern 5 — the `Location: evil.com` read as open

```text
the failure: Location: evil.com (no scheme/ //) resolves RELATIVE to the
             origin -> target.com/evil.com — same-origin, NOT the gap
the fix:     the cross-origin forms are //evil.com / https://evil.com /
             \\evil.com — a bare host resolves relative
```

## Anti-pattern 6 — treating the class as the flag

```text
the failure: a confirmed Location: <canary> on a challenge whose flag is
             the LAUNDERED trust — the OAuth code, the internal fetch, the
             bot's session — the open-redirect alone is the surface
the fix:     the class confirm is hop-0; route to chain-routes.md for the
             laundered-trust flag
```

## Anti-pattern 7 — the one-param test

```text
the failure: testing ONLY `next` — the vocabulary is ~100 names; the real
             param is url/redirect_uri/RelayState/post_logout_redirect_uri/
             back/Referer/stored
the fix:     the param-inventory sweep — the vocabulary over the endpoints
```

## Anti-pattern 8 — the one-carrier test

```text
the failure: testing ONLY the Location header — missing the meta-refresh,
             the JS-nav, the location.hash, the stored, the Referer
the fix:     the carrier-matrix — Location/Refresh/meta/JS/hash/stored/Referer
```

## Anti-pattern 9 — a javascript: "confirm" without the sink check

```text
the failure: "javascript:alert(1) reached the sink" — but the browser
             blocks location.href='javascript:...' — a client-side block,
             not a server-side confirm
the fix:     the verbatim sink-value is the evidence; the firing is a
             separate browser-split check — record both
```

## Anti-pattern 10 — the single-arm falsifier

```text
the failure: "https://evil.com -> Location: / — the class is closed"
             — ONE arm's failure isn't the class falsifier
the fix:     the falsifier needs EVERY arm -> Location: <safe> — the
             uniform response across the whole filter-bypass corpus
```

## Anti-pattern 11 — the encoded-only sweep

```text
the failure: only trying the ENCODED forms — %2f, %5c, %2540 — missing the
             raw //, /\, @ forms that the filter's raw-string check misses
the fix:     sweep BOTH the raw and encoded arms — the decode-order gap
             is which stage the filter checks
```

## Anti-pattern 12 — the invent-a-parse model

```text
the failure: assuming the filter parses a certain way without measuring —
             "the @ should bypass it" — but the server's urlparse reads it
             differently
the fix:     measure the parser — send the differential arms and READ which
             parse the filter uses by which arms pass
```

## Anti-pattern 13 — the unsupported-claim record

```text
the failure: "the redirect is open" without the verbatim Location in
             --response — the gate asserts evidence is a substring
the fix:     --evidence 'Location: https://evil.com' --response '<the raw>'
             — the substring-check is enforced
```

## Anti-pattern 14 — the SSRF-confusion

```text
the failure: a fetcher-URL param treated as an open-redirect — the server
             FETCHES the URL, doesn't redirect to it — wrong class
the fix:     read the response — fetched-CONTENT = SSRF; Location: =
             open-redirect
```

## Anti-pattern 15 — the repeated-fingerprint

```text
the failure: a Location: / on arm-N treated as a NEW signal — it's the
             SAME safe response — the uniform response is the falsifier,
             not a new arm to try
the fix:     record each arm's Location; a repeat of the safe-fingerprint
             is a measured-negative, not a new hypothesis
```
