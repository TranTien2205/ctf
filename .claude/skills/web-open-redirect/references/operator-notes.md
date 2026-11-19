# Operator notes — the running notes an operator keeps

## The session-notes template

```text
=== open-redirect session — <challenge> ===
target: <BASE>
the surface: <endpoint>?<param>=
the carrier: <Location | meta | JS | Refresh | stored | Referer>
the fingerprint: <the ONE Location on the canary>
the filter-shape: <startswith | contains | endswith | parse | scheme | decode>
the arms tried:
  <arm-1> -> <the-Location>
  <arm-2> -> <the-Location>
  ...
the verdict: <confirms | negative | falsifies>
the chain: <the laundered-trust or the standalone answer>
the evidence: <the verbatim Location>
```

## The running-hypothesis notes

```text
h-or-1: /login?next= is an unchecked redirect
  the-probe: curl -si '$BASE/login?next=...' | grep -i location
  the-status: testing
  the-fingerprint: Location: / (a forced-relative)
  the-arms-tried: //evil.com, /\evil.com, https://t.com@evil.com
  the-verdict: pending — the subdomain arm next
```

## The arms-tried ledger — the falsifier's evidence

```text
the arms-tried table — record EVERY arm + its Location:
| the arm | the Location | the verdict |
| https://evil.com | Location: / | blocked |
| //evil.com | Location: / | blocked |
| /\evil.com | Location: / | blocked |
| https://t.com@evil.com | Location: / | blocked |
| https://t.com.evil.com | Location: https://t.com.evil.com | ** CANDIDATE ** |
```

## The chain-note — the launder observation

```text
the open-redirect confirms: Location: //evil.com on /login?next=
the chain-surface: the OAuth authorize's redirect_uri allowlist is
                   client-app.com — and client-app.com/redirect IS an
                   open-redirect -> the launder is open
the chain-evidence: the canary's access log: GET /?code=...
```

## The negative-notes — the closed surfaces

```text
the closed surfaces — record which surfaces are dead:
  /login?next=     -> the host-allowlist holds (Location: t.com/ on all)
  /out?url=        -> a fetcher — the fetched-CONTENT is returned (SSRF)
  /back<-Referer   -> the Referer is checked — Location: /default
```

## The operator-checklist — the running pass

```text
[ ] the param vocabulary swept on the endpoints
[ ] the carriers checked — Location/Refresh/meta/JS/Referer/stored
[ ] the fingerprint read — the filter shape named
[ ] the matching arms swept — the filter-shape family
[ ] the verdicts recorded — each arm's verbatim Location
[ ] the chain checked — the laundered-trust route
[ ] the falsifier recorded — the uniform safe + the arms-tried
[ ] the post-probe evidence a substring of the response
```
