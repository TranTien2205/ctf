# GCM nonce reuse — the forbidden attack — deep

GCM reusing a nonce leaks the GHASH authentication subkey H: two tagged ciphertexts under one nonce let you forge tags for arbitrary new ciphertexts. tools/gcm_nonce.py runs the algebra.

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

Falsifier — no nonce ever repeats (checked across all captured records) or the tag check precedes every decrypt attempt uniformly: the forbidden attack has no input. Reclassify toward tag truncation or a different class.

## Highest-cost traps

- The recovered H is one of a few algebraic candidates — test each against a third record.
- AAD differences change the tag equation; include --aad1/--aad2 whenever present.
- Nonce reuse also XORs the CTR keystream — the plaintext recovery part is crib-drag territory (ctr-nonce-reuse.md).

## Commands

```bash
python3 tools/gcm_nonce.py --ct1 <h> --tag1 <h> --ct2 <h> --tag2 <h>
python3 tools/gcm_nonce.py --selftest
```

## Cross-references

`tools-gcm-nonce.md` · `ctr-nonce-reuse.md` · `mac-forgery.md`
