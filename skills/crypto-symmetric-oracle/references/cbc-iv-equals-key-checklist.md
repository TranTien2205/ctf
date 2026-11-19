# CBC IV = key and related IV bugs — operational checklist

If the service reuses the key as the IV (or exposes it through the decrypt error channel), three chosen-ciphertext queries recover the key. Rarer than padding oracles but instant when it fires.

## Checklist

- [ ] Take a real ciphertext C1|C2|C3. Send C1|0|C1 for decryption: P'1 = D(C1) XOR IV, P'3 = D(C1) XOR C1, so P'1 XOR P'3 = C1 XOR IV = IV-key relationship.
- [ ] If IV == key, P'1 XOR P'3 recovers the key directly.
- [ ] For predictable IVs: submit guess plaintext; if it matches a captured ciphertext, the guess was right (chosen-plaintext verification).
- [ ] Always check the error response for echoed plaintext — that alone is the oracle.

## Abort conditions

- The classic exploit needs the service to SHOW you decrypted garbage — a silent decrypt gives nothing.
- Predictable-IV attacks need chosen plaintext and the ability to compare ciphertexts for equality — useless when each encryption is salted.

## Falsifier

Falsifier — the decrypt endpoint never echoes plaintext and the IV is random per message: no IV-equality signal exists. Drop to padding-oracle or reclassify.

## Cross-references

`cbc-bitflip.md` · `cbc-padding-oracle.md`
