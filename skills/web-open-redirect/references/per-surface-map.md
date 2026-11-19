# Per-surface map — the surface-to-file navigation

## The endpoint-surface → the file

| The endpoint-surface | The file |
|---|---|
| `/login`/`/signin` | `per-endpoint.md`, `per-param.md` |
| `/logout`/`/signout` | `per-endpoint.md` |
| `/oauth/*`/`/sso`/`/saml/*` | `per-endpoint.md`, `chain-routes.md` |
| `/out`/`/goto`/`/link` | `per-endpoint.md` |
| `/img`/`/fetch`/`/proxy` | `per-endpoint.md`, `chain-routes.md` |
| `/back`/`/previous` | `per-endpoint.md`, `stored-and-referer.md` |
| `/error`/`/403`/`/404` | `per-endpoint.md` |
| `/checkout`/`/payment` | `per-endpoint.md` |
| `/share`/`/qr`/`/deeplink` | `per-endpoint.md` |
| the stored set-then-fire | `stored-and-referer.md` |
| the Referer-derived | `stored-and-referer.md` |

## The filter-surface → the file

| The filter-shape | The file |
|---|---|
| `startswith('/')` | `per-check.md`, `per-vector.md` |
| `contains('target.com')` | `per-check.md`, `per-target.md` |
| `endswith('target.com')` | `per-check.md`, `per-target.md` |
| `hostname == / netloc ==` | `parser-differentials.md`, `per-check.md` |
| `scheme in [http,https]` | `per-check.md`, `per-vector.md` |
| the regex | `per-check.md` |
| the decode-order | `encoding-attacks.md` |
| the framework-check | `framework-matrix.md` |
| a hardened/residual | `evasion.md` |

## The carrier-surface → the file

| The carrier | The file |
|---|---|
| `Location:` header | `detection.md`, `evidence-rules-deep.md` |
| `Refresh:` header | `client-side.md`, `edge-cases.md` |
| `<meta refresh>` | `client-side.md` |
| `location.href`/`replace`/`assign` | `client-side.md` |
| `location.hash` | `client-side.md` |
| the stored | `stored-and-referer.md` |
| the Referer-derived | `stored-and-referer.md` |
| the DOM-source | `client-side.md` |

## The chain-surface → the file

| The chain | The file |
|---|---|
| the OAuth launder | `chain-routes.md`, `per-route.md`, `multi-step-chains.md` |
| the SSRF-fetch-follow | `chain-routes.md`, `per-route.md` |
| the XSS-scheme-sink | `chain-routes.md`, `per-route.md` |
| the bot-visit | `chain-routes.md`, `per-route.md` |
| the phishing launder | `chain-routes.md`, `exploitation.md` |
| the CRLF split | `edge-cases.md`, `per-route.md` |
| the Referer-leak | `per-route.md`, `edge-cases.md` |
| the token-fragment | `per-route.md`, `multi-step-chains.md` |

## The verdict-surface → the file

| The verdict | The file |
|---|---|
| the candidate confirm | `evidence-rules-deep.md` |
| the strong-negative | `negative-results-deep.md` |
| the weak-negative | `negative-results.md`, `negative-map.md` |
| the falsifier | `falsifiers-deep.md`, `per-falsifier.md` |
| the troubleshoot | `troubleshoot.md` |
| the mistake | `common-mistakes.md`, `anti-patterns.md` |
