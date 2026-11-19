# Evidence variant — what counts, ranked by strength

## The ranked ladder

```
flag{ / CTF{                       the flag — strongest, the goal
impact: forged token works         exploit confirmed
class: predict == held-back        the state is real — the gate
fingerprint: gcd/BM matched        a hypothesis — a lead, not proof
outputs: a stream collected        the premise — nothing yet
```

## The non-evidence

- `flag{` in the description — not recovered.
- `predict` on a training output — verifies nothing.
- one lucky match — not a recovery.
- "the state looks right" — not bit-for-bit.
- uniform/random-looking — not predictable.
- a recovered `a`,`c` never verified — a candidate.

## The two gates

- **class** (`predict==held`) — proves the state is real. Recordable as
  `--evidence-kind class`.
- **impact** (`flag{`/`forged works`) — proves exploit. `--evidence-kind
  impact`.

## The response requirement

`--evidence` must be a substring of `--response` — the bytes the evidence
was read from. The gate asserts the substring, so the quote is checked,
not trusted.

## The record

```bash
post-probe <ch> --verdict confirms --hypothesis-id <id> --class crypto-prng \
  --evidence-kind class --evidence 'predict==held' --response '<bytes>'
pre-flag <ch> --value 'flag{...}' --evidence '<the bytes>'
```

## The honest note

A `catalogue` class has no local chain cards — the corpus is the field
procedure. `predict==held` is the only proof a state is real; never
assert a recovery from a return value alone.
