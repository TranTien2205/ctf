# Length extension — hash(secret||msg) forgery

A MAC built as sha1/sha256/md5 of secret||message is forgeable: the hash's internal state after the message is the digest itself — continue it with your appended data.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| MAC = raw SHA-1/SHA-256/MD5 of secret||data | length-extension applies | tools/crypto_attack.py length-extension |
| You know the message and the secret LENGTH (or can brute a small range) | extension possible | forge digest |
| MAC = HMAC (keyed envelope) | NOT vulnerable | reclassify — see mac-forgery |
| Sponge hash: SHA-3, Keccak, BLAKE2 | NOT vulnerable | reclassify |

## Steps

1. Confirm the construction: hash(secret || known_message) with a Merkle-Damgard hash.
2. python3 tools/crypto_attack.py length-extension --hash sha1 --mac <original-mac> --secret-len <N> --orig <known-msg> --append '&admin=1'
3. The tool emits the forged MAC AND the exact bytes to submit (msg || glue-padding || appended).
4. Submit the extended message with the forged MAC; acceptance = class impact confirmed.
5. If the secret length is unknown, iterate --secret-len over the plausible range (usually 8..64) — the server tells you which length forged correctly.

## Falsifier

Falsifier — the forged MAC is rejected under every secret length tried: the MAC is HMAC, a keyed PRF, or a sponge hash, or the server appends after your data (suffix MACs don't extend forward).

## Traps

- Glue padding must be computed over secret_len + len(orig) — off-by-one there is the top reason a correct attack fails.
- The forged message contains non-printable pad bytes — submit it as raw bytes/hex, not through a form field that strips them.
- hash(secret||msg) where the hash is SHA-512/256 or SHA-256 truncated: extension still works if the hash retains state — truncated digests lose the tail of state.
- Server-side normalization (lower-casing, key reordering) breaks the byte-exact replay — test with a no-op append first.

## Commands

```bash
python3 tools/crypto_attack.py length-extension --hash sha1 --mac <mac> --secret-len 16 --orig 'user=guest' --append '&admin=1'
python3 tools/crypto_attack.py length-extension --help
```

## Cross-references

`tools-length-extension.md` · `mac-forgery.md` · `hmac-vs-raw-mac.md`
