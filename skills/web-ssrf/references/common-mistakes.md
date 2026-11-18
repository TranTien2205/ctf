# Common mistakes — the ways SSRF work goes wrong

The failure-modes that burn probes and produce false claims —
each with the fix.

---

## 1. Treating "no callback" as "no fetch"

```text
MISTAKE: send the canary → silence → conclude "not ssrf" → move on
FIX:     silence is ambiguous — egress-blocked, queue-deferred,
         wrong-scheme, no-fetch — the INTERNAL-probe decides:
         url=http://127.0.0.1:1/ → a refused-error means the
         fetcher exists and dialed → the class lives even with
         zero callback — egress-blocked.md
```

## 2. Claiming a flag from a flag-shaped string in source/config

```text
MISTAKE: reading "flag{...}" in a source-file and reporting it
FIX:     the flag must pass hooks.py pre-flag from a LIVE response
         or supplied artifact — a flag-shaped-string in code is a
         candidate — read it THROUGH the ssrf (file:///path → the
         response carrying it) then verify — the provenance is the
         difference between "found" and "saw"
```

## 3. Spray-checking ip-encodings without naming the check

```text
MISTAKE: trying 30 ip-encodings hoping one works — burning the
         5-probe budget on the same mechanism
FIX:     the encoding-family is ONE mechanism — 5 probes then
         SWITCH MECHANISM — the check-type comes first: string/
         resolution/fetch-time — the encoding answers the string-
         check — the rebind answers the resolution-check — pick
         the family that answers the CHECK not the family that's
         longest
```

## 4. Reading only the 200-body — the error-blind spot

```text
MISTAKE: fetch fails → "error" → move on — never reading the body
FIX:     the error-body carries the content — "fetch failed: <the
         bytes>" — the red-island flag came back inside a 401's
         message-field — EVERY response gets read — the error is
         often the channel — error-analysis.md
```

## 5. Forgetting the User-Agent tells you the fetcher

```text
MISTAKE: probing gopher:// on a python-requests app — scheme-dead
         from the start
FIX:     the callback's User-Agent IS the fetcher — read it FIRST —
         curl → gopher lives; python-requests → http-only; java →
         jar/netdoc — the fetcher-matrix picks the scheme-list —
         one callback answers the whole "which schemes" question
```

## 6. Assuming 127.0.0.1 is the only loopback

```text
MISTAKE: "127.0.0.1 blocked" → conclude loopback-dead → give up
FIX:     localhost, 127.1, [::1], 0.0.0.0, the nip-names, the
         decimal/hex/octal forms — the loopback-family is a dozen
         names — the check blocked ONE — url-parsing.md §1
```

## 7. Missing the deferred-fetch — the "it didn't fetch" trap

```text
MISTAKE: register a webhook → "nothing happened" → move on
FIX:     the fetch is SCHEDULED — check the results-page later —
         or trigger the event — or the manual "test" button — the
         deferred-shape's fetch is on a clock — webhook-deferred.md
```

## 8. The single-request mindset — missing the request-composition

```text
MISTAKE: "the url only fetches one page" — stopping at the GET
FIX:     the fetch is a REQUEST — crlf-injection composes a whole
         request — the gopher-http subcommand composes a request —
         header-control, method-control, body-control — the
         request-composition is the stronger primitive
```

## 9. Never testing the loopback's own routes

```text
MISTAKE: sweeping internal-IPs but never the app itself
FIX:     http://127.0.0.1:<app-port>/admin — the loopback-bound
         admin-route — the most common flag-home — the app's own
         ip passes its own localhost-check — try /admin /flag
         /actuator/env /metrics /status /console
```

## 10. Ignoring the redirect-chain

```text
MISTAKE: "the url is whitelisted" → give up
FIX:     the whitelist checks the ENTRY — the redirect-hops may
         not re-validate — an open-redirect on the allowed-domain
         bounces you anywhere — redirect-chains.md
```

## 11. Not distinguishing refused from timeout

```text
MISTAKE: "connection failed" — lumping refused+timeout together
FIX:     refused = host-ALIVE-port-closed → sweep other ports on
         the same host — timeout = filtered/dead — they're
         different diagnoses — the port-sweep only proceeds on
         refused — timeout on EVERY port means the subnet is wrong
```

## 12. Trusting "the file was fetched" — without checking WHICH file

```text
MISTAKE: file:///etc/passwd works → "file-read confirmed" → then
         file:///flag fails → confused
FIX:     the file-permission matters — /flag may be root-only —
         the fetcher's uid decides — /etc/passwd reads because
         world-readable — a perm-error ≠ no-file — the permission-
         oracle — and the flag may be on a different path entirely
```

## 13. The unicode/case miss — the check-vs-resolver gap

```text
MISTAKE: only trying lowercase-ascii bypasses
FIX:     the domain-resolver is case+unicode-insensitive — the
         check's string-compare may not be — the EXAMPLE.COM,
         fullwidth, punycode, %-encoded-letters family
```

## 14. Skipping the open-redirect hunt

```text
MISTAKE: "no open-redirect on the allowed-domain" — after one look
FIX:     the open-redirect may be on a parameter not tested —
         /redirect /out /goto /link /track /r /u /away /leave —
         crawl the allowed-domain's routes — the redirect-endpoint
         list — redirect-chains.md §3
```

## 15. The metadata-assumption — "it's cloud" without evidence

```text
MISTAKE: jumping to 169.254.169.254 because "it's probably cloud"
FIX:     check /proc/self/cgroup + /etc/resolv.conf via file://
         first — docker/k8s markers say "container" not "cloud" —
         the metadata-IP times out on non-cloud — the cloud-shape
         is confirmed by the metadata-response not assumed
```

## 16. Forgetting the second-order — the stored-url

```text
MISTAKE: testing url=params but never stored-urls
FIX:     the webhook/feed/avatar/profile-url is a STORE-then-fetch
         — the check-runs-at-write vs fetch-at-read — the deferred
         channel — webhook-deferred.md
```

## 17. Treating "the fetch worked" as "the fetch controls everything"

```text
MISTAKE: fetch confirmed → assume all-controls → try to set
         method+headers+body
FIX:     the fetch's shape is the app's — the method is usually
         GET — headers are the app's — body is usually none —
         header/method/body control needs crlf-injection or
         gopher-composition — test what's controllable — the
         fetch-context is usually fixed
```

## 18. Not binding the evidence — the substring-check fails

```text
MISTAKE: claim "ssrf confirmed, response showed X" → post-probe
         rejects — the quote isn't in the response
FIX:     http_probe binds request+response — the --response field
         IS the bytes — the quote must be verbatim — don't retype
         or paraphrase — the tool emits the command — paste it
```

## 19. The timing-noise error

```text
MISTAKE: one slow-response → "port-22 is open!" → false-positive
FIX:     timing is noisy — measure 3x, use the median — a single
         slow response is jitter — the differential needs a stable
         baseline — measure the refused-baseline first, then the
         target-port — the DIFFERENCE is the signal not the number
```

## 20. Classifying the crlf-split as "just ssrf"

```text
MISTAKE: the url's %0d%0a splits the request → keep treating as
         ssrf → the smuggling-primitive unexplored
FIX:     when control-chars reach the wire the class CHANGES —
         request-composition → desync → web-request-smuggling —
         the weather-app card — classify by mechanism not surface
```
