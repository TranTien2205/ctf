# Detection surface deep — the artifacts, the reads, the signals

## The file types

| Type | The read | The signal |
|---|---|---|
| `.pem`/`.der`/`.crt`/`.key` | `RSA.importKey` | `n` bits, `e`, `d`/`p`/`q`/`dp`/`dq`/`qInv` |
| `.json` | `json.load` | `n`,`e`,`c`/`d`/`phi`/`dp` fields |
| `.txt` | `re.findall(r'\d{20,}')` | the `n`,`e`,`c` integers |
| `.py` | read `keygen`/`chal`/`gen` | `next_prime`,`seed`,`getPrime(d)`,`p-1`,`e=3`,no pad,`m2=a·m1+b`,`dp`,`dq`,`qInv`,`redact` |
| `.bin` | `xxd`/`strings`/`binwalk` | an embedded key/`n` |
| `.pcap` | `tshark`/`scapy` | a handshake `n`,`e`, a `c` |

## The observable signals

| Signal | The attack |
|---|---|
| `e`=3/5/17 | `small-e`/`hastad`/`franklin-reiter` |
| `e`≈`n` | `wiener`/`boneh-durfee` |
| `n`s share `p` | `batch-gcd` |
| `p-1` smooth | `pollard-pm1` |
| `p` bits | `coppersmith` |
| `d`/`phi`/`dp`/`qInv` | `factor-from-d`/`crt` |
| `m2=a·m1+b` | `franklin-reiter` |
| `gcd(e,phi)>1` | `eth-root` |
| `n`=p²/prime | degenerate |

## The verify

`pow(m,e,n)==c` / `p*q==n`.
