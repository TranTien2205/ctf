# ECB prefix vs suffix oracles — case catalogue

Byte-at-a-time works when your input PRECEDES the secret (suffix). When the secret precedes your input, the method inverts — recover backwards, or via a fixed suffix oracle.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | encrypt(input || secret) | suffix oracle | standard byte-at-a-time |
| 2 | encrypt(secret || input) | prefix oracle | reverse byte-at-a-time |
| 3 | encrypt(prefix || input || suffix) | sandwiched | combined alignment+suffix |

## Falsifier

Falsifier — neither prefix nor suffix is controllable (your input is wholly inside fixed material): the oracle doesn't reach the secret.

## Coverage notes

- A random per-request prefix only defeats alignment, not the method — if a fixed suffix exists, attack backwards.
- Prefix recovery is rarer; double-check your orientation before implementing.
- Multiple secrets in one ciphertext can be independent — measure each region separately.

## Cross-references

`ecb-byte-at-a-time.md` · `block-alignment.md`
