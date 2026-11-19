# ECB cut-and-paste / block substitution — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Encrypted token is a concatenation of blocks, each a field | block substitution applies | map field offsets, then splice |
| You can request tokens for chosen input values | chosen-plaintext block source | mint a block holding the value you need |
| Token has a fixed prefix you cannot change | boundary alignment needed | pad your input so the target field starts a block |

## Falsifier

Falsifier — the token carries a MAC over the whole ciphertext or the plaintext, or decrypt rejects spliced blocks: the construction is authenticated and cut-and-paste dies. Reclassify to mac-forgery or authenticated-boundary.
