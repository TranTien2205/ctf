# Checklist — the run-list

## Before any attack

- [ ] `selfcheck.py` green.
- [ ] generator identified (`lcg`/`lfsr`/`mt`/`xorshift`/`seed`).
- [ ] outputs collected and normalized (raw, consecutive).
- [ ] usable-output count checked against the attack's floor.

## The gates

- [ ] LCG? `m` known → `lcg-recover`; `m`? → `lcg-unknown-modulus`;
      truncated → `lcg-truncated`.
- [ ] LFSR? taps unknown → `berlekamp-massey` → `lfsr-recover`/`predict`.
- [ ] MT? 624 words → `mt19937-clone`.
- [ ] xorshift? 4 words → `xorshift128`.
- [ ] seed? bounded window → enumerate.

## Solve + verify

- [ ] right attack id + real flags.
- [ ] `predict == held-back` BEFORE trusting the state.
- [ ] `flag{`/`CTF{` or the forged object.

## Record

- [ ] `post-probe` verbatim (evidence ⊆ response).
- [ ] `../field-notes.md` entry.
- [ ] `classify_solve`/`attempts` filed.
- [ ] `decide.py` if stuck.
