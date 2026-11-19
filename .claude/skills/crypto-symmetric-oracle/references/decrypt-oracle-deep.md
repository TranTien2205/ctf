# Decrypt oracle — the richest shape — deep

A real decrypt oracle (submit ciphertext, get plaintext) usually ends the challenge. The work is understanding what the service will and won't decrypt.

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

Falsifier — the decrypt endpoint never returns plaintext and gives only valid/invalid answers: it was a padding oracle all along, not a decrypt oracle.

## Highest-cost traps

- Replay protection (rejects exact duplicate CT) is trivially bypassed by an IV tweak that changes nothing semantically.
- Plaintext echo might contain the flag — inspect the whole response.
- An authorization layer after decrypt is a separate check — the crypto worked.

## Commands

```bash
python3 tools/pad_oracle.py --selftest
```

## Cross-references

`cbc-padding-oracle.md` · `cbc-bitflip.md`
