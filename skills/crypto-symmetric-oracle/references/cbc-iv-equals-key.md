# CBC IV = key and related IV bugs

If the service reuses the key as the IV (or exposes it through the decrypt error channel), three chosen-ciphertext queries recover the key. Rarer than padding oracles but instant when it fires.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Decryption errors echo raw plaintext back | error-channel oracle | key recovery in 3 blocks |
| Source shows iv = key or iv derived from key | IV=key construction | key recovery |
| IV predictable but independent (counter, timestamp) | predictable-IV chosen plaintext | verify guessed plaintext encryptions |

## Steps

1. Take a real ciphertext C1|C2|C3. Send C1|0|C1 for decryption: P'1 = D(C1) XOR IV, P'3 = D(C1) XOR C1, so P'1 XOR P'3 = C1 XOR IV = IV-key relationship.
2. If IV == key, P'1 XOR P'3 recovers the key directly.
3. For predictable IVs: submit guess plaintext; if it matches a captured ciphertext, the guess was right (chosen-plaintext verification).
4. Always check the error response for echoed plaintext — that alone is the oracle.

## Falsifier

Falsifier — the decrypt endpoint never echoes plaintext and the IV is random per message: no IV-equality signal exists. Drop to padding-oracle or reclassify.

## Traps

- The classic exploit needs the service to SHOW you decrypted garbage — a silent decrypt gives nothing.
- Predictable-IV attacks need chosen plaintext and the ability to compare ciphertexts for equality — useless when each encryption is salted.

## Commands

```bash
python3 tools/crypto_attack.py crib-drag --ct1 <h> --ct2 <h> --crib 'flag{'
```

## Cross-references

`cbc-bitflip.md` · `cbc-padding-oracle.md`
