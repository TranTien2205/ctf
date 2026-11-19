# Probe order — cheapest first

## The read order

1. **Parse** — extract outputs; free.
2. **Fingerprint** — name the generator; the gcd/BM/clone tests are cheap.
3. **Count** — `len(outputs)` against the floor; free.
4. **Normalize** — hex→int, float→word; free.
5. **Params** — `m`/`a`/`c`/taps/`low-bits`/seed-window from source.
6. **Attack** — only after the gates pass.

## The attack order

- **LCG**: `lcg-recover` (closed form, m known) → `lcg-unknown-modulus`
  (gcd trick) → `lcg-truncated` (lattice, heaviest).
- **LFSR**: `lfsr-predict` (taps known) → `berlekamp-massey` →
  `lfsr-recover` → `lfsr-predict`.
- **MT/xorshift**: direct — the count IS the gate.
- **seed**: bound the window → enumerate.

## The verify — last

`predict == held-back` — cheap, mandatory.
