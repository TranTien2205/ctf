# length-extension driver — forged MACs — operational checklist

tools/crypto_attack.py length-extension builds the padded extended message and its forged MAC in one shot — the glue padding is handled for you.

## Checklist

- [ ] Confirm the MAC is raw-hash(secret||m) — HMAC won't extend.
- [ ] Determine the secret length (from source, or iterate a range).
- [ ] python3 tools/crypto_attack.py length-extension --hash sha1 --mac <m> --secret-len <n> --orig 'a=b' --append '&admin=1'.
- [ ] Submit the emitted message bytes (msg||glue||append) and forged MAC.
- [ ] Accepted = forge confirmed; record with post-probe.

## Abort conditions

- --secret-len is the KEY length, not the MAC length.
- The emitted message contains non-printable glue pad bytes — submit raw, not through forms.
- Truncated digests (sha512/256) still extend; full state is what matters.

## Falsifier

Falsifier — every forged MAC rejects at every tried secret length: construction is HMAC/sponge, or the server appends after your data.

## Cross-references

`length-extension.md` · `hmac-vs-raw-mac.md`
