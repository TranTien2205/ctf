# tools/pad_oracle.py — CBC padding-oracle driver — deep

HTTP driver for Vaudenay: feeds each candidate byte to the oracle URL, tracks the validity distinguisher, and prints the recovered plaintext.

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

Falsifier — the distinguisher never fires (all requests look the same): the oracle doesn't exist, or the regex/status is wrong. Re-verify the distinguisher on a hand-crafted pad before blaming the tool.

## Highest-cost traps

- The IV is part of --ct — omitting it shifts every block by one and the attack silently fails.
- A regex that matches the ERROR page instead of the OK page inverts the loop — check which answer you're keying on.
- --max-requests too low aborts mid-byte; too high can burn the rate limit permanently.

## Commands

```bash
python3 tools/pad_oracle.py --selftest
python3 tools/pad_oracle.py --ct <h> --url 'https://t/d?c={CT}' --ok-regex 'OK'
```

## Cross-references

`cbc-padding-oracle.md` · `response-distinguishers.md`
