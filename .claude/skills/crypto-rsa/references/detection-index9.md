# Detection index9 — the final detection index

## The artifact → the read → the signal

| Artifact | The read | The signal |
|---|---|---|
| `.pem`/`.der`/`.crt`/`.key` | `RSA.importKey` | `n`,`e`,`d`/`p`/`q`/`dp`/`dq`/`qInv` |
| `.json` | `json.load` | `n`,`e`,`c`/`d`/`phi`/`dp` fields |
| `.txt` | `re.findall` | the integers + counts |
| `.py` | `grep`/`read` | `next_prime`,`seed`,`getPrime(d)`,`p-1`,`e=3`,no pad,`a·m1+b`,`dp`,`dq`,`qInv`,`redact` |
| `.bin` | `xxd`/`strings` | an embedded key/`n` |
| `.pcap` | `tshark`/`scapy` | `n`,`e`,`c` |
| live `nc`/`host` | `nc`/`requests` | a `c`/`sig`/oracle |

## The arithmetic → the signal

- `n`,`e`,`c` counts → `batch-gcd`/`hastad`/`common-modulus`.
- `e` size → `wiener`/`boneh-durfee`/`small-e`/`eth-root`.
- `gcd(e,phi)` → `eth-root`.
- `n` square/prime → degenerate.
- `m^e` vs `n` → `small-e`/`nth-root`.

## The route

`attack-table*.md` → `per-bound.md` → `crypto_attack.py <id>` → `verify*`.
