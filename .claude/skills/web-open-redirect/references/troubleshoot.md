# Troubleshoot — when the redirect test doesn't produce the expected signal

## The param produces no Location at all

| The symptom | The check | The fix |
|---|---|---|
| `200 render` on `?next=` | the param name is wrong | sweep the vocabulary — `param-inventory` |
| `400 Bad Request` on the canary | the param validation rejects the format | the param IS a redirect but strict; try the relative form `next=/x` to confirm the carrier |
| `302` to a fixed page | the param isn't read | a different param name; the two-step |
| a `Location` with no canary | the param sets the path, host forced | the host-force — try the `//`/substring/userinfo arms |

## The Location is safe on every arm

| The symptom | The check | The fix |
|---|---|---|
| `Location: /` on every bypass | the allowlist/relative-force holds | the class falsifier — record uniform-negative |
| `Location: https://target.com/x` on every bypass | a host-force | try the suffix/userinfo/`@`/`%5c` arms |
| `Location: ` the param VERBATIM but same-origin | the param resolves relative | `Location: evil.com` resolves `target.com/evil.com` — not the gap; the `//`/`scheme` forms |

## The bypass arm produces an unexpected result

| The symptom | The check | The fix |
|---|---|---|
| `//evil.com` → `Location: /` | the `//` is blocked | try `\/evil.com`/`\\evil.com`/`/\evil.com` — the backslash arms |
| `evil.com\@target.com` → `Location: /` | the `\@` normalized | try `evil.com%40target.com` (encoded) / `evil.com?@target.com` |
| `%5c` decoded wrong | the server doesn't decode `%5c` to `\` | try a double-encode `%255c`, or the raw `\` |
| the encoded arm is rejected | the server validates the ENCODED string | the check reads the encoded form literally — the decoded-form reaches the browser |
| `javascript:` → `Location: javascript:` but no fire | a browser-block | the scheme reaches the sink but the browser blocks — a `data:`/`blob:` alternative |

## The client-side surface produces no signal

| The symptom | The check | The fix |
|---|---|---|
| no meta/JS in the response | the redirect is server-side OR a different carrier | `curl -s` for meta; the bundle for `location.*` |
| the JS nav uses `location.hash` | a fragment-param | `#next=` — the fragment isn't sent to the server; the JS reads it |
| a DOM-sink the curl can't trigger | the param is read by JS, not rendered server-side | read the bundle — `bundle_miner.py`; feed `?next=` + run the page |
| the `location.href` value is escaped | sanitized | a different sink / a `javascript:` vs `data:` scheme split |

## The chain doesn't launder

| The symptom | The check | The fix |
|---|---|---|
| `Location: evil.com` confirms but no code | the OAuth allowlist is strict | the open-redirect is on the WRONG host — it must be ON an allowlisted `redirect_uri` domain |
| the fetcher doesn't reach the canary | the fetcher doesn't follow redirects | the SSRF-chain is dead — a direct-URL fetcher, not a redirect-follower |
| the bot visits but no exfil | the bot doesn't run JS / a meta redirect | the bot needs a JS-capable client — `web-chromedriver` |
| the `javascript:` is stripped | the client-side sanitizer | a different scheme / a different sink |

## The tool/probe-level issues

| The symptom | The check | The fix |
|---|---|---|
| `redirect_probe.py` reports nothing | the URL/param args | `--url` must have the param; `--param` to pin one |
| curl follows the redirect | `-L`/`--location` | drop `-L`; use `-si` + `grep -i location` |
| the canary isn't URL-encoded | the `?`/`&`/`%` in the canary break the param | `urllib.parse.quote` the canary |
| a redirect-loop | the param lands on ANOTHER redirect | follow the chain hop-by-hop with `follow=False` |

## The "is this even the class" checks

| The observation | The reclassification |
|---|---|
| the param is fetched not redirected | `web-ssrf` — the fetcher surface |
| the param is a DOM-sink with a scheme | `web-xss` — the javascript:/data: twin |
| the `Location` carries a CRLF | `web-request-smuggling`/header-injection |
| the redirect_uri is the OAuth surface | `web-oauth-sso` |
| the param reaches a meta-refresh | the client-side twin — still this class |
