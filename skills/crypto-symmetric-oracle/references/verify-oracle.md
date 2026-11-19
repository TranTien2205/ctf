# Verify oracle — tag checking as a distinguisher

A verify endpoint that answers 'tag good' vs 'tag bad' is an oracle on the authentication side. Timing in the compare function, truncation, and acceptance of malformed tags all leak.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Verify endpoint reports ok/invalid only | verify oracle | truncation and timing probes |
| Early-exit byte compare in source | timing leaks position | byte-at-a-time tag |
| Verify accepts structurally invalid inputs | parser gap | forge via parser |

## Steps

1. Check tag length enforcement: submit tags of length 1..full; find the minimum accepted.
2. Time rejects for tags differing in each prefix position — early-exit reveals how much is correct.
3. Try structurally malformed tags (empty, non-hex, negative lengths) — parser bugs often accept them.
4. Recover the tag byte-by-byte through the timing oracle if the compare is early-exit.

## Falsifier

Falsifier — the verify is constant-time, full-length, type-strict: no oracle. Reclassify toward key-path or different class.

## Traps

- Timing measurement needs MANY samples (50+) and baseline correction — a single diff proves nothing.
- Truncation acceptance is a bug, not an attack: it only helps if you still have to produce the accepted prefix.
- Parser-level accepts (None, '') sometimes bypass the check entirely — always try the trivial cases first.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`mac-forgery.md` · `response-distinguishers.md`
