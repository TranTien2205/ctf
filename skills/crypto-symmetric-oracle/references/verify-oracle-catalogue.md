# Verify oracle — tag checking as a distinguisher — case catalogue

A verify endpoint that answers 'tag good' vs 'tag bad' is an oracle on the authentication side. Timing in the compare function, truncation, and acceptance of malformed tags all leak.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Verify endpoint reports ok/invalid only | verify oracle | truncation and timing probes |
| 2 | Early-exit byte compare in source | timing leaks position | byte-at-a-time tag |
| 3 | Verify accepts structurally invalid inputs | parser gap | forge via parser |

## Falsifier

Falsifier — the verify is constant-time, full-length, type-strict: no oracle. Reclassify toward key-path or different class.

## Coverage notes

- Timing measurement needs MANY samples (50+) and baseline correction — a single diff proves nothing.
- Truncation acceptance is a bug, not an attack: it only helps if you still have to produce the accepted prefix.
- Parser-level accepts (None, '') sometimes bypass the check entirely — always try the trivial cases first.

## Cross-references

`mac-forgery.md` · `response-distinguishers.md`
