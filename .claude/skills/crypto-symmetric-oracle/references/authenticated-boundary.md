# Authenticated modes — where the class closes

GCM, ChaCha20-Poly1305, and encrypt-then-MAC kill every malleability oracle. The honest skill boundary: recognize when NOTHING here applies and route out early.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Tag verified before any decryption | oracles closed | nonce reuse or key-path only |
| Tampering uniformly rejected | no distinguisher | reclassify |
| Nonce/IV visible and reused across records | authenticated but misused | gcm-nonce-reuse or ctr reuse |
| Key/seed/IV leaked in source or params | not a crypto attack — read the flag | direct decryption |

## Steps

1. Test the tamper response once: corrupt mid-ciphertext and check whether ANY response difference exists (status/body/timing).
2. If none: the remaining surface is nonce reuse, key material, or a misuse of the primitive — check each.
3. Key in the handout (a --key flag, a hardcoded constant) is not an oracle attack — just decrypt.
4. When genuinely closed, record the negative: 'authenticated before decrypt, no nonce reuse observed' and hand back to the router.

## Falsifier

Falsifier — corrupt ciphertext is rejected identically for every offset tested: the class is closed. Continuing to probe malleability is budget waste.

## Traps

- Constant-time compare makes TIMING identical too — do not confuse 'no timing signal' with 'bug present'.
- A 96-bit GCM nonce with random generation collides after ~2^32 messages — rarely reachable in CTF scale.
- Some CTF handouts label the mode 'AES-256' without the mode — check ciphertext length vs plaintext length and tag presence.

## Commands

```bash
python3 tools/crypto_attack.py list
python3 tools/gcm_nonce.py --selftest
```

## Cross-references

`oracle-shapes.md` · `gcm-nonce-reuse.md` · `class-boundary.md`
