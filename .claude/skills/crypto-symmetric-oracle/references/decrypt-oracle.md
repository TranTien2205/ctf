# Decrypt oracle — the richest shape

A real decrypt oracle (submit ciphertext, get plaintext) usually ends the challenge. The work is understanding what the service will and won't decrypt.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Decrypt endpoint returns plaintext | full oracle | decrypt the flag |
| Decrypt rejects the captured ciphertext | replay protection | malleate it |
| Decrypt applies authorization on the plaintext | decrypt-then-check | forge via malleability |

## Steps

1. Try the obvious: submit the captured ciphertext verbatim.
2. If rejected, malleate: bit-flip a non-critical field or splice blocks so it's a NEW ciphertext of a similar plaintext.
3. If it returns plaintext, decrypt the flag directly — the challenge is done.
4. If it applies checks on plaintext content, use bit-flip to adjust the plaintext to pass.

## Falsifier

Falsifier — the decrypt endpoint never returns plaintext and gives only valid/invalid answers: it was a padding oracle all along, not a decrypt oracle.

## Traps

- Replay protection (rejects exact duplicate CT) is trivially bypassed by an IV tweak that changes nothing semantically.
- Plaintext echo might contain the flag — inspect the whole response.
- An authorization layer after decrypt is a separate check — the crypto worked.

## Commands

```bash
python3 tools/pad_oracle.py --selftest
```

## Cross-references

`cbc-padding-oracle.md` · `cbc-bitflip.md`
