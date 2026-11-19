# First-hour deep — the reads, the output, the budget

## The reads

- `crypto_attack.py list` — the inventory + `lll_backend`.
- `RSA.importKey` — `n` bits, `e`, private fields.
- `re.findall` — the `n`,`e`,`c` integers + counts.
- `keygen`/`chal` grep — the tell (`next_prime`,`seed`,`getPrime(d)`,`e=3`,
  no pad,`a·m1+b`,`dp`,`dq`,`qInv`,`redact`,`print`).
- The counts/`e` size/`gcd`/square/`m^e` — the discriminating reads.
- `attack-table.md` → `per-bound.md` → `crypto_attack.py <id>` → `pow`/`p*q`.

## The output

A signal, a bound, an attack — and the sheet filled.

## The falsifier-first rule

Read `per-bound.md` *before* the attack — the bound is a theorem; a measurement
below it closes the attack. The first attack is cheap; the lattice is last.

## The budget

`decide.py` — 5 probes/15 active min per class, 25/45 per challenge. `n` is
one signal — don't reset the budget by relabelling.

## The record

`post-probe` on every confirm/falsify; `../field-notes.md` after.
