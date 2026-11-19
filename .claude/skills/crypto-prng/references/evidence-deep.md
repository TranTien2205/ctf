# Evidence deep — what each artifact actually proves

## The evidence ladder

1. **output** — you collected `o0,...,ok`. Proves: the stream exists.
   Proves nothing about predictability.
2. **fingerprint** — the gcd/BM/clone-test matched a generator. Proves: a
   hypothesis, not a recovery.
3. **`predict == held-back`** — the recovered state emitted a held-back
   output bit-for-bit. **Proves: the state is real.** This is the class
   evidence.
4. **impact** — the predicted token authenticated / the keystream
   decrypted the flag / the predicted roll won. **Proves: exploit.**
5. **`flag{`/`CTF{`** — read from the response or the decrypted bytes.
   The flag. Post through `hooks.py`.

## What is NOT evidence

- A `flag{`-shaped string in the challenge description.
- `predict` matching ONE output by coincidence — reproduce a sequence.
- A recovered `a`,`c` that you never verified on a held-back output.
- A state that "looks right" — bit-for-bit only.
- Statistical uniformity — not predictability.
- The word "random" or "secure" in comments — a label, not a fact.

## The `post-probe` shape

```bash
python3 tools/hooks.py post-probe <challenge> --verdict confirms \
  --hypothesis-id <id> --class crypto-prng \
  --evidence-kind class|impact \
  --evidence 'predict_next == held_back_word' \
  --response '<the bytes the evidence was read from>'
```

`confirms` requires the evidence to be a substring of `--response` — the
gate checks it.

## The flag gate

```bash
python3 tools/hooks.py pre-flag <challenge> --value 'flag{...}' --evidence '<the response/artifact bytes it was read from>'
```

Never a flag without the response bytes that contain it.

## The record discipline

`attempts/` for every falsifier (what proved dead + the precondition that
reopens it). `classify_solve` for the solve → chain card + `../field-notes.md`
`confirmed`.
