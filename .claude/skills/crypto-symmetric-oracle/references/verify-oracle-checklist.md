# Verify oracle — tag checking as a distinguisher — operational checklist

A verify endpoint that answers 'tag good' vs 'tag bad' is an oracle on the authentication side. Timing in the compare function, truncation, and acceptance of malformed tags all leak.

## Checklist

- [ ] Check tag length enforcement: submit tags of length 1..full; find the minimum accepted.
- [ ] Time rejects for tags differing in each prefix position — early-exit reveals how much is correct.
- [ ] Try structurally malformed tags (empty, non-hex, negative lengths) — parser bugs often accept them.
- [ ] Recover the tag byte-by-byte through the timing oracle if the compare is early-exit.

## Abort conditions

- Timing measurement needs MANY samples (50+) and baseline correction — a single diff proves nothing.
- Truncation acceptance is a bug, not an attack: it only helps if you still have to produce the accepted prefix.
- Parser-level accepts (None, '') sometimes bypass the check entirely — always try the trivial cases first.

## Falsifier

Falsifier — the verify is constant-time, full-length, type-strict: no oracle. Reclassify toward key-path or different class.

## Cross-references

`mac-forgery.md` · `response-distinguishers.md`
