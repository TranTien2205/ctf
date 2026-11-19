# Troubleshoot (deep) — the full failure-resolution guide

## The param produces no Location

| The symptom | The cause | The fix |
|---|---|---|
| `200 render` on `?next=` | `next` isn't the param | sweep the vocabulary — `param-inventory` |
| `400` on the canary | the param validation rejects the URL-format | send `next=/x` (relative) to confirm the carrier |
| `302` to a fixed page | the param isn't read | a different param; the stored/Referer surface |
| `Location: <the-param>` but same-origin | the param resolves relative | `evil.com` -> `target.com/evil.com` — send `//evil.com`/`https://evil.com` |
| a `Location:` on a 200/201 | a REST 'created-at' hint | not a nav redirect — a different carrier |

## The Location is safe on every arm

| The symptom | The cause | The fix |
|---|---|---|
| `Location: /` on all arms | the allowlist/relative-force holds | the class falsifier — record the arms + close |
| `Location: https://target.com/` on all arms | a host-force | the `@`/subdomain/substring arms |
| a `Location: /` on `//evil.com` | the `//` blocked | `/\evil.com`, `\\evil.com`, `/%5cevil.com` |
| a `Location: /` on `\@` | the `\@` normalized | `evil.com%40target.com`, `evil.com?@target.com`, `evil.com#@target.com` |
| a `Location: /` on `javascript:` | the scheme rejected | `data:`, `vbscript:`, `file:`, `intent:`, a client-side sink |
| a `Location: /` on `%252f` | the double-decode normalized | a single-encode `%2f`, or the raw `\`/`/` |

## The bypass arm produces an unexpected result

| The symptom | The cause | The fix |
|---|---|---|
| `Location: /` on `//evil.com` | the `//`-block | the `/\`/`\\`/`%5c`/`%2f` arms |
| `Location: the-param-decoded` but still safe | the check runs AFTER decode | the RAW form — the check is on the decoded |
| `Location: /` on `evil.com\@target.com` | the `\@` normalized | `evil.com%40target.com`, `evil.com?@target.com` |
| the subdomain arm passes a suffix-check but not the parse | the suffix matched but the parse didn't | `eviltarget.com` — the no-boundary arm |
| the substring arm passes but the host is the canary | a CANDIDATE | post-probe confirms |

## The client-side surface produces no signal

| The symptom | The cause | The fix |
|---|---|---|
| no meta/JS in the response | a server-side carrier OR a different endpoint | check `Location:`; check the bundle |
| the JS nav uses `location.hash` | a fragment-param | `#next=` — the JS reads the hash |
| the `location.href` value is escaped | the JS sanitizes | a different sink; a `javascript:`/`data:` scheme-split |
| the param is a DOM-source the curl can't trigger | the param is read by JS not rendered | read the bundle — `bundle_miner.py`; feed `?next=` in a browser |

## The chain doesn't launder

| The symptom | The cause | The fix |
|---|---|---|
| `Location: evil.com` but no OAuth code | the allowlist is strict | the open-redirect must be ON the allowlisted domain — find one |
| the fetcher doesn't reach the internal host | the fetcher doesn't follow redirects | a direct-URL SSRF — `web-ssrf`; the redirect-follow is a specific fetcher behavior |
| the `javascript:` reaches the sink but no fire | a browser-block | a `data:`/`blob:` alternative; the verbatim sink-value is the candidate |
| the bot visits but the meta doesn't fire | the bot doesn't run JS | the bot needs a JS-capable client — `web-chromedriver` |
| the redirect resolves same-origin | `Location: evil.com` is relative | a `//evil.com`/`https://evil.com`/`\\evil.com` — the cross-origin forms |

## The tool/probe issues

| The symptom | The cause | The fix |
|---|---|---|
| `redirect_probe.py` reports nothing | the `--url` lacks the param | pass `--url 'BASE/ep'` + `--param <name>` |
| curl follows the redirect | `-L`/`--location` | drop `-L`; `-si` + `grep -i location` |
| the canary's `?`/`&`/`%` break the param | unencoded | `urllib.parse.quote` the canary |
| a redirect-loop | the param chains another redirect | follow hop-by-hop with `follow=False` |
| the URL in the Location is unreadable | a non-ASCII/encoded | the verbatim bytes — `curl -si` not `-s` |

## The "is this the class" checks

| The observation | The real class |
|---|---|
| the param is FETCHED not redirected | `web-ssrf` |
| the `javascript:` reaches a DOM-sink | `web-xss` |
| the `redirect_uri` is the OAuth surface | `web-oauth-sso` |
| a `%0d%0a` splits the `Location:` | `web-request-smuggling`/header-injection |
| the `\@`/`%5c` parse-gap is the mechanism | `web-parser-differential` |
| a reflected `?next=` in a link the victim clicks | `web-xss`/the phishing surface |
