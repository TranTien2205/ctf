# Detection matrix — signal → class-confidence → the next probe

## The signal matrix

| The signal | The confidence | The next probe |
|---|---|---|
| a `?next=`/`?url=`/`?redirect=` param | low — a name-match | the canary |
| a 302 on the param | low — the redirect exists | read the `Location:` |
| `Location: <canary>` | CANDIDATE — the oracle | post-probe `confirms` |
| `Location: /`/`Location: <safe>` | strong-negative for that arm | the filter-shape arms |
| no `Location` on the param | weak-negative | a different param name |
| a meta-refresh carrying the param | client-side candidate | the `content=` value |
| a `location.href` carrying the param | client-side candidate | the DOM-sink value |
| a `Refresh:` header carrying the param | a header-carried candidate | the `Refresh:` value |
| `Location: <partial-canary>` | a path/host-force fingerprint | the matching arms |
| `Location: target.com.evil.com` | CANDIDATE — a subdomain-gap | post-probe `confirms` |

## The endpoint-signal matrix

| The endpoint | The expected param | The signal |
|---|---|---|
| `/login` | `next`/`return`/`goto` | `Location: <the-param>` |
| `/logout` | `next`/`post_logout_redirect_uri` | `Location: <the-param>` |
| `/oauth/authorize` | `redirect_uri`/`callback` | `Location: <the-param>` |
| `/out`/`/goto`/`/link` | `url`/`link`/`target` | `Location: <the-param>` |
| `/img`/`/fetch`/`/proxy` | `url`/`img`/`uri` | the fetched-CONTENT (SSRF) vs `Location:` |
| `/back` | (the Referer) | `Location: <the-Referer>` |
| `/error`/`/403` | `next`/`url` | `Location: <the-param>` |
| `/checkout` | `successUrl`/`cancelUrl` | `Location: <the-param>` |
| `/share`/`/qr` | `url`/`link`/`data` | the embedded-URL |

## The carrier-signal matrix

| The carrier | The detection | The evidence |
|---|---|---|
| `Location:` header | `curl -si | grep -i '^location'` | the verbatim `Location:` |
| `Refresh:` header | `curl -si | grep -i '^refresh'` | the verbatim `Refresh:` |
| meta refresh | `curl -s | grep -i 'refresh'` | the verbatim `content=` |
| JS nav | `curl -s | grep -i 'location'` | the verbatim `location.*=` |
| `location.hash` | the bundle's `location.hash` read | the parsed fragment |
| the DOM-source | `bundle_miner` / the JS grep | the `location.* = <param>` |

## The fingerprint-signal matrix — the Location shape

| The `Location:` on the canary | The signal | The verdict |
|---|---|---|
| `Location: https://attacker.invalid` | the verbatim canary | CANDIDATE |
| `Location: //evil.com` | the scheme-relative canary | CANDIDATE |
| `Location: https://evil.com` | the simple-host canary | CANDIDATE |
| `Location: https://target.com.evil.com` | the substring/subdomain-gap | CANDIDATE |
| `Location: https://evil.com/target.com` | the substring-in-path-gap | CANDIDATE |
| `Location: https:evil.com` | the scheme-no-// | CANDIDATE |
| `Location: /` | forced-relative | safe arm — try the bypass |
| `Location: /dashboard` | a fixed safe | safe arm |
| `Location: https://target.com/login` | an allowlisted | safe arm |
| `Location: evil.com` | relative — resolves same-origin | NOT the gap — a negative |
| `Location: javascript:alert(1)` | a JS-scheme | candidate — the firing is browser-split |
| `Location: data:text/html,...` | a data:-scheme | candidate |

## The confidence-ladder

```text
lowest:   the param name exists
low:      the param reaches a carrier
medium:   the carrier returns + a `Location:`/`content=`/`location=`
high:     the carrier carries the canary (the oracle)
highest:  the laundered-trust fires (the impact)
```

## The verdict-signal matrix

| The verdict | The signal |
|---|---|
| `confirms` | `Location: <canary>` verbatim — the oracle |
| `negative` | `Location: <safe>` on the canary — a strong-negative |
| `falsifies` | `Location: <safe>` on EVERY arm — the class falsifier |
| `weak-negative` | no `Location`/meta/JS on a guessed param — the name is wrong |
| `candidate` | a partial-fingerprint — the matching arms pending |

## The matrix-record

`detect: <signal>: <the-confidence>: <the-next-probe>` — each observed
signal + its confidence rung + the one probe it implies.
