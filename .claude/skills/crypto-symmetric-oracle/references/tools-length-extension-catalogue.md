# length-extension driver — forged MACs — case catalogue

tools/crypto_attack.py length-extension builds the padded extended message and its forged MAC in one shot — the glue padding is handled for you.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | --hash sha1/sha256/md5 | the Merkle-Damgard hash | pick by construction |
| 2 | --mac = original tag hex | the captured MAC | over the known message |
| 3 | --secret-len = key length | key size | iterate if unknown |
| 4 | --orig = known message | the captured plaintext | the base for extension |
| 5 | --append = your tail bytes | the forgery payload | e.g. '&role=admin' |

## Falsifier

Falsifier — every forged MAC rejects at every tried secret length: construction is HMAC/sponge, or the server appends after your data.

## Coverage notes

- --secret-len is the KEY length, not the MAC length.
- The emitted message contains non-printable glue pad bytes — submit raw, not through forms.
- Truncated digests (sha512/256) still extend; full state is what matters.

## Cross-references

`length-extension.md` · `hmac-vs-raw-mac.md`
