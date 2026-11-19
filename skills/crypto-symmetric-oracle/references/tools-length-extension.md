# length-extension driver — forged MACs

tools/crypto_attack.py length-extension builds the padded extended message and its forged MAC in one shot — the glue padding is handled for you.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --hash sha1/sha256/md5 | the Merkle-Damgard hash | pick by construction |
| --mac = original tag hex | the captured MAC | over the known message |
| --secret-len = key length | key size | iterate if unknown |
| --orig = known message | the captured plaintext | the base for extension |
| --append = your tail bytes | the forgery payload | e.g. '&role=admin' |

## Steps

1. Confirm the MAC is raw-hash(secret||m) — HMAC won't extend.
2. Determine the secret length (from source, or iterate a range).
3. python3 tools/crypto_attack.py length-extension --hash sha1 --mac <m> --secret-len <n> --orig 'a=b' --append '&admin=1'.
4. Submit the emitted message bytes (msg||glue||append) and forged MAC.
5. Accepted = forge confirmed; record with post-probe.

## Falsifier

Falsifier — every forged MAC rejects at every tried secret length: construction is HMAC/sponge, or the server appends after your data.

## Traps

- --secret-len is the KEY length, not the MAC length.
- The emitted message contains non-printable glue pad bytes — submit raw, not through forms.
- Truncated digests (sha512/256) still extend; full state is what matters.

## Commands

```bash
python3 tools/crypto_attack.py length-extension --hash sha1 --mac <m> --secret-len 16 --orig 'u=g' --append '&a=1'
python3 tools/crypto_attack.py length-extension --help
```

## Cross-references

`length-extension.md` · `hmac-vs-raw-mac.md`
