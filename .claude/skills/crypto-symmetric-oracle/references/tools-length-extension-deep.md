# length-extension driver — forged MACs — deep

tools/crypto_attack.py length-extension builds the padded extended message and its forged MAC in one shot — the glue padding is handled for you.

## Mechanism internals

The attack surface is defined by which byte the service lets you reach and which bit of the response leaks. The three invariants that hold across every variant of this attack: (1) the distinguisher must be measurable before the loop starts, (2) each recovered byte is confirmed by an exact-match answer — never a probabilistic one, (3) the loop stops at the measured boundary (block edge, secret length, tag width), not where the bytes 'look done'.

## Boundary conditions

- If the response is compressed before encryption, alignment dies — check for gzip/deflate first.
- If the oracle answers 'ok' for structurally invalid input, the parser layer is the bug, not the crypto.
- Rate limits convert a 40k-request loop into days — measure throughput and bound --max-requests.
- Nonce reuse at the block level is different from per-message reuse — align by absolute counter.
- A MAC checked before decryption closes every malleability route in this file.
- When the same tool flag is documented differently in two modules, tools/<name>.py --help is authoritative.

## Falsifier

Falsifier — every forged MAC rejects at every tried secret length: construction is HMAC/sponge, or the server appends after your data.

## Highest-cost traps

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
