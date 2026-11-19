# Decrypt oracle — the richest shape — case catalogue

A real decrypt oracle (submit ciphertext, get plaintext) usually ends the challenge. The work is understanding what the service will and won't decrypt.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Decrypt endpoint returns plaintext | full oracle | decrypt the flag |
| 2 | Decrypt rejects the captured ciphertext | replay protection | malleate it |
| 3 | Decrypt applies authorization on the plaintext | decrypt-then-check | forge via malleability |

## Falsifier

Falsifier — the decrypt endpoint never returns plaintext and gives only valid/invalid answers: it was a padding oracle all along, not a decrypt oracle.

## Coverage notes

- Replay protection (rejects exact duplicate CT) is trivially bypassed by an IV tweak that changes nothing semantically.
- Plaintext echo might contain the flag — inspect the whole response.
- An authorization layer after decrypt is a separate check — the crypto worked.

## Cross-references

`cbc-padding-oracle.md` · `cbc-bitflip.md`
