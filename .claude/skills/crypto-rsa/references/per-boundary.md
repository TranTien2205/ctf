# Per-boundary map — the edge → the class inside it

## The edges

| The edge | Inside crypto-rsa? |
|---|---|
| `n`,`e`,`c` + a leak | yes — the core class |
| a socket printing `n`,`e`,`c` | yes — transport, not oracle |
| a socket computing on `m` | no — `crypto-symmetric-oracle` |
| `g`,`h=g^x`,a curve | no — `crypto-ecc-dlog` |
| a keystream/seed | no — `crypto-prng` |
| `d`/`phi`/`dp`/`p`,`q` held | yes — `factor-from-d`/`rsa-decrypt` terminal |
| a faulty+correct sig | yes — `crt` Bellcore |
| an arbitrary signing oracle | no — signature-forgery class |
| `n=p²`/`n` prime | yes — degenerate RSA |
| `n=p·q·r` multi-prime | yes — adjust `phi` |
| `e=3`,padded `m` | yes — but `coppersmith`,not root |
| a web endpoint using RSA | no — the web class owns it |

## The boundary tests

- "decrypt this" → the RSA classes.
- "compute this for me" → the oracle class.
- "recover `x` from `g^x`" → dlog.
- "predict the stream" → prng.
- "get `p`,`q` or `d` or `φ` or `m`" → crypto-rsa.

## The rule

If the recoverable target is `p`,`q`,`d`,`φ`,or `m` from `n`,`e`,`c` — this
class. If the target is `x` from `g^x`, a keystream, or a service's output — the
neighbour class.
