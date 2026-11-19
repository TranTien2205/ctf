# Evidence catalogue — artifact → strength → the gate → the file

## The artifacts ranked

| Artifact | Strength | Gate | File |
|---|---|---|---|
| `flag{`/`CTF{` in response | the flag | `pre-flag` | `evidence*` |
| forged token/roll works | impact | `post-probe` impact | `evidence*` |
| `predict == held-back` | the state real | `post-probe` class | `verify*` |
| recovered `state`/`a`,`c`/`m` | a candidate | verify first | `verify*` |
| `gcd`→`m`/BM `(w,taps)` | a hypothesis | — | `detection*` |
| a collected stream | the premise | — | `detection*` |

## The two recordable kinds

- **`class`** — `predict==held` proves the state is real. The gate for
  claiming a recovery.
- **`impact`** — the forged/decrypted/won object. The gate for the flag
  chain.

## The response-bytes rule

`--evidence` is a substring of `--response` — the gate asserts it. Hand-
assembling means pasting the bytes — `tools/web/http_probe.py` holds
request+response together for web oracles.

## The non-evidence list

- `flag{` in the description text.
- `predict` matching a training output.
- one lucky match — not a sequence.
- "looks plausible" / "looks random" / "uniform".
- a return value never verified.

## The falsifier records

`negative-map`/`negative-results*` — every `predict!=held`/`gcd→0`/
`L≈n/2` recorded with the mechanism + `reopen_if`.

## The honest note

`crypto-prng` is a `catalogue` class — no local chain cards. The corpus
is standard mechanism + field procedure — `predict==held` is the only
proof.
