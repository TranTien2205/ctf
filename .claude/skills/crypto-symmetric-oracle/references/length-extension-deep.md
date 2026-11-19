# Length extension — hash(secret||msg) forgery — deep

A MAC built as sha1/sha256/md5 of secret||message is forgeable: the hash's internal state after the message is the digest itself — continue it with your appended data.

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

Falsifier — the forged MAC is rejected under every secret length tried: the MAC is HMAC, a keyed PRF, or a sponge hash, or the server appends after your data (suffix MACs don't extend forward).

## Highest-cost traps

- Glue padding must be computed over secret_len + len(orig) — off-by-one there is the top reason a correct attack fails.
- The forged message contains non-printable pad bytes — submit it as raw bytes/hex, not through a form field that strips them.
- hash(secret||msg) where the hash is SHA-512/256 or SHA-256 truncated: extension still works if the hash retains state — truncated digests lose the tail of state.

## Commands

```bash
python3 tools/crypto_attack.py length-extension --hash sha1 --mac <mac> --secret-len 16 --orig 'user=guest' --append '&admin=1'
python3 tools/crypto_attack.py length-extension --help
```

## Cross-references

`tools-length-extension.md` · `mac-forgery.md` · `hmac-vs-raw-mac.md`
