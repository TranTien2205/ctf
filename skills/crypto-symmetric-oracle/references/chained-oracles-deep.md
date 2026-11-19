# Chained oracles — combining two distinguishers — deep

Sometimes neither oracle alone suffices: a verify oracle gives 1 bit but the decrypt endpoint gives length. Chain them — each oracle answers what the other can't.

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

Falsifier — neither oracle discriminates the needed bit: the attack requires a channel neither provides. Re-run detection for a missed one.

## Highest-cost traps

- The verify oracle's bit is the pad-oracle's bit under a different name — check they differ meaningfully.
- Rate limits differ per endpoint — budget per endpoint separately.

## Commands

```bash
python3 tools/pad_oracle.py --selftest
python3 tools/ecb_oracle.py --selftest
```

## Cross-references

`cbc-padding-oracle.md` · `verify-oracle.md`
