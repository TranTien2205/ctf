# Decrypt oracle — the richest shape — operational checklist

A real decrypt oracle (submit ciphertext, get plaintext) usually ends the challenge. The work is understanding what the service will and won't decrypt.

## Checklist

- [ ] Try the obvious: submit the captured ciphertext verbatim.
- [ ] If rejected, malleate: bit-flip a non-critical field or splice blocks so it's a NEW ciphertext of a similar plaintext.
- [ ] If it returns plaintext, decrypt the flag directly — the challenge is done.
- [ ] If it applies checks on plaintext content, use bit-flip to adjust the plaintext to pass.

## Abort conditions

- Replay protection (rejects exact duplicate CT) is trivially bypassed by an IV tweak that changes nothing semantically.
- Plaintext echo might contain the flag — inspect the whole response.
- An authorization layer after decrypt is a separate check — the crypto worked.

## Falsifier

Falsifier — the decrypt endpoint never returns plaintext and gives only valid/invalid answers: it was a padding oracle all along, not a decrypt oracle.

## Cross-references

`cbc-padding-oracle.md` · `cbc-bitflip.md`
