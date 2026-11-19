# ECB cut-and-paste / block substitution — summary

ECB blocks are independent: a ciphertext block decrypts the same wherever it sits. Forge a message by swapping, replaying, or re-ordering blocks — the standard target is role/admin fields in encrypted profiles.

## Signal → route

- Encrypted token is a concatenation of blocks, each a field → map field offsets, then splice
- You can request tokens for chosen input values → mint a block holding the value you need
- Token has a fixed prefix you cannot change → pad your input so the target field starts a block

## Falsifier

Falsifier — the token carries a MAC over the whole ciphertext or the plaintext, or decrypt rejects spliced blocks: the construction is authenticated and cut-and-paste dies. Reclassify to mac-forgery or authenticated-boundary.
