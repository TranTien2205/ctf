# Length extension — hash(secret||msg) forgery — surface variants

A MAC built as sha1/sha256/md5 of secret||message is forgeable: the hash's internal state after the message is the digest itself — continue it with your appended data.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| MAC = raw SHA-1/SHA-256/MD5 of secret||data | length-extension applies | tools/crypto_attack.py length-extension |
| You know the message and the secret LENGTH (or can brute a small range) | extension possible | forge digest |
| MAC = HMAC (keyed envelope) | NOT vulnerable | reclassify — see mac-forgery |
| Sponge hash: SHA-3, Keccak, BLAKE2 | NOT vulnerable | reclassify |

## Variant-specific traps

- Glue padding must be computed over secret_len + len(orig) — off-by-one there is the top reason a correct attack fails.
- The forged message contains non-printable pad bytes — submit it as raw bytes/hex, not through a form field that strips them.
- hash(secret||msg) where the hash is SHA-512/256 or SHA-256 truncated: extension still works if the hash retains state — truncated digests lose the tail of state.
- Server-side normalization (lower-casing, key reordering) breaks the byte-exact replay — test with a no-op append first.

## Falsifier

Falsifier — the forged MAC is rejected under every secret length tried: the MAC is HMAC, a keyed PRF, or a sponge hash, or the server appends after your data (suffix MACs don't extend forward).

## Cross-references

`tools-length-extension.md` · `mac-forgery.md` · `hmac-vs-raw-mac.md`
