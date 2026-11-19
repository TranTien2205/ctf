# Detection variant 4 — the reads by output format

## The integer-output reads

- `d`/`x`/`k` scalar → verify `x·G == Q`/`g^x == h`.
- Multiple `x` candidates → CRT or re-check `ord`.

## The lattice-output reads

- A short vector — not `d` directly; `d` is in the vector's coordinates.
- `d` plausible but fails verify → the lattice solved a wrong HNP.

## The curve-output reads

- `smart_attack`/`singular_ec` return `x` — verify on the original curve.
- `ec.py` fake-curve responses → `d mod ord_i` each, then CRT.

## The oracle-output reads

- A point `d·P'` → the response *is* the evidence.
- `pow`/`mul` responses → the scalar-recovery step, then CRT.

## The flag reads

- `flag{`/`CTF{` in decoded bytes — the proof of impact.
- The scalar is `class` evidence; the flag is `impact`.
