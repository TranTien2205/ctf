# Probe map — the probe-to-observation navigation

## The probe → the observation → the next probe

| The probe | The observation | The next probe |
|---|---|---|
| `?next=https://evil.com` | `Location: <canary>` | post-probe `confirms` → `chain-routes.md` |
| `?next=https://evil.com` | `Location: /` | the `//`/`\`/`%5c` arms |
| `?next=https://evil.com` | `Location: https://target.com/` | the `@`/substring/subdomain arms |
| `?next=https://evil.com` | no `Location` | a different param / the meta/JS carrier |
| `?next=//evil.com` | `Location: //evil.com` | CANDIDATE — post-probe |
| `?next=//evil.com` | `Location: /` | the `/\`/`\\`/`%5c` arms |
| `?next=/\evil.com` | `Location: /\evil.com` | CANDIDATE — the `\`->`/` |
| `?next=https://t.com@evil.com` | `Location: https://t.com@evil.com` | CANDIDATE — the userinfo |
| `?next=https://t.com.evil.com` | `Location: https://t.com.evil.com` | CANDIDATE — the subdomain |
| `?next=https://evil.com/t.com` | `Location: https://evil.com/t.com` | CANDIDATE — the substring |
| `?next=https:evil.com` | `Location: https:evil.com` | CANDIDATE — the scheme-no-// |
| `?next=https%3a%2f%2fevil.com` | `Location: https://evil.com` | CANDIDATE — the decode-order |
| `?next=javascript:alert(1)` | `Location: javascript:` | the browser-split check |
| `?url=<param>` (a meta) | `content="0;url=<canary>"` | a client-side-twin candidate |
| `?url=<param>` (a JS) | `location.href="<canary>"` | a client-side-twin candidate |
| `Referer: <canary>` `/back` | `Location: <canary>` | a Referer-derived candidate |
| `?next=` set + a later flow | `Location: <canary>` on the fire | a stored-redirect candidate |

## The observation → the verdict map

| The observation | The verdict |
|---|---|
| `Location: <canary>` verbatim | `confirms` — the class oracle |
| `Location: <safe>` on one arm | `negative` — that arm blocked |
| `Location: <safe>` on ALL arms | `falsifies` — the class closed |
| no `Location` on a param | `negative` (weak) — wrong param |
| a meta/JS carries the canary | `confirms` — the client-side twin |
| a meta/JS escaped | `negative` — the twin is closed |
| the chain's downstream fires | `confirms` — `evidence-kind impact` |

## The probe → the file map

| The probe | The file |
|---|---|
| the param sweep | `param-inventory.md`, `per-param.md` |
| the canary | `quick-reference.md`, `field-manual.md` |
| the fingerprint | `decision-table.md`, `detection-matrix.md` |
| the bypass arms | `filter-bypass-deep.md`, `per-vector.md`, `per-check.md`, `payload-dictionary.md` |
| the encode-order | `encoding-attacks.md` |
| the client-side | `client-side.md` |
| the stored/Referer | `stored-and-referer.md` |
| the chain | `chain-routes.md`, `per-route.md`, `multi-step-chains.md` |
| the verdict record | `evidence-rules-deep.md` |
