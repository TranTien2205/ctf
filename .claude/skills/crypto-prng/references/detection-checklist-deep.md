# Detection checklist deep — every read, annotated

## The artifact reads — expanded

- [ ] **Generator type named or fingerprinted** — `mt19937`/`xorshift`/
  `LFSR`/`LCG` in source; else run the gcd/BM/clone fingerprint. If it's a
  `os.urandom`/`secrets`/`/dev/urandom` — wrong class.
- [ ] **Outputs extracted raw and consecutive** — the exact stream order,
  no sorting, no dedup, no gaps. A gap is a missing `x_i` — the affine
  structure misaligns.
- [ ] **Output shape noted** — int / hex / float / bit / `mod n` / `>>b`.
  The shape decides raw-vs-truncated-vs-normalize.
- [ ] **Oracle endpoints noted** — `GET /token`/`/nonce`/`/rand`/`/roll` —
  where consecutive outputs come from, and whether calls interleave.
- [ ] **Seed/init visible** — `seed=`, `srand`, `init_genrand`, a
  timestamp/pid — the seed-search hook.

## The gate reads — expanded

- [ ] **Count meets the floor** — `len(outputs)` against 3/6/required/
  2·w/624/4. Under → collect more or pick a different attack.
- [ ] **Outputs normalized to raw ints** — hex→`int(x,16)`, float→word,
  base64→decode, `mod n`→the raw problem. One non-raw value poisons the
  solve.
- [ ] **Params identified** — `m`,`a`,`c` for LCG (source or recovered);
  `width`,`taps` for LFSR (or leave to BM); `--low-bits` the DROPPED count;
  seed window bounded.
- [ ] **Alignment confirmed** — the outputs are adjacent in the stream
  (no other caller consumed the generator). A shared `random` module
  breaks this.
- [ ] **Reseed ruled out** — no `seed()`/`srand()` inside the window.

## The route reads — expanded

- [ ] **Family picked** — `lcg`/`lfsr`/`mt`/`xorshift`/`seed` — from the
  fingerprint, not a guess.
- [ ] **Attack picked** — `lcg-recover` vs `lcg-unknown-modulus` vs
  `lcg-truncated` differ only in WHAT is known; `lfsr-recover` vs
  `lfsr-predict` differ only in whether taps are known. The param-known
  column chooses.
- [ ] **Command composed** — real flags from `payload-dictionary*`;
  `--outputs`/`--bits`/`--outs`/`--taps`/`--width`/`--low-bits`/`--count`.
- [ ] **Verification planned** — which output is held back, and how
  `predict` is compared.

## The close reads — expanded

- [ ] **`predict == held` plan** — held-back output chosen, comparison is
  bit-for-bit.
- [ ] **flag shape expected** — `flag{`/`CTF{` from the forged/decrypted
  object, not the state.
- [ ] **`post-probe` shape ready** — `--evidence` a verbatim quote,
  `--response` the bytes.

## The meta reads

- [ ] The class is PRNG, not `crypto-symmetric-oracle`/`misc-encoding`.
- [ ] No CSPRNG/seed-entropy source confirmed.
- [ ] The budget is tracked — 5 probes / 15 min per mechanism.
