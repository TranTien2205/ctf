# Token forgery — from oracle to forged object — deep

Most CTF oracle challenges end at a forged token: an admin cookie, a signed profile, a role=admin field. The path from oracle to forge is mechanical once the primitive is proven.

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

Falsifier — the token construction resists its intended primitive (authenticated, HMAC, sponge) and the forgery is rejected: re-run detection, the construction was misidentified.

## Highest-cost traps

- A token that VALIDATES but doesn't grant the privilege means you forged the wrong field — map the privilege source first.
- Tokens often carry timestamps/expiry; the forgery must keep those fields valid.
- URL-encoding eats raw pad bytes — submit as hex or raw body where the endpoint accepts it.

## Commands

```bash
python3 tools/ecb_oracle.py --selftest
python3 tools/crypto_attack.py length-extension --hash sha1 --mac <m> --secret-len <n> --orig <o> --append '<a>'
```

## Cross-references

`ecb-cut-and-paste.md` · `cbc-bitflip.md` · `length-extension.md`
