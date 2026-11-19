# Per-boundary catalogue — the class boundaries, indexed

## The boundaries

| Boundary | Out | In | File |
|---|---|---|---|
| `misc-encoding-carrier` | `+/=`/hex/`01`/`.-` — `enc_detect` | letters-only `ct` | `class-boundary.md`,`encoding-*.md` |
| `crypto-symmetric-oracle` | `mod`/`block`/`oracle`/`iv` — `crypto_attack` | letter-`σ`/`k`/`π` | `class-boundary.md`,`per-boundary*.md` |
| `crypto-prng` | `state`/`seed`/`mod`/`tap` — `crypto_attack` | letter-`σ`/`k`/`π` | `class-boundary.md` |
| `crypto-rsa`/`crypto-ecc-dlog` | `N`,`e`,`p`,`q`/`G`,`P`,`n`,`d` — `crypto_attack` | letter-`σ`/`k`/`π` | `class-boundary.md` |

## The boundary rule

The *charset* decides — a letter-only letter-transform → `crypto-classical`;
a structured alphabet → `misc-encoding-carrier`; a `mod`/`big-int`/`curve` →
a modern class.

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
