# Checklist variant — the run-list, compact

## Before any attack

- [ ] `selfcheck.py` green.
- [ ] group named (`p a b G n`/`g p` + `ord`).
- [ ] `z` convention picked.

## The gates

- [ ] `r` dedupe → `ecdsa-nonce-reuse`?
- [ ] `k` bound? → `hnp-ecdsa`.
- [ ] `(t,u)`? → `hnp`.
- [ ] `smoothness --n ord` → `pohlig-hellman`?
- [ ] `x` bound? → `bsgs`.
- [ ] `Δ`/`#E` → `singular`/`smart`?
- [ ] validation probe → invalid curve?

## Solve + verify

- [ ] right command + real flags.
- [ ] `x·G == Q`/`pow == h` BEFORE trusting the scalar.
- [ ] `flag{`/`CTF{` from decoded bytes.

## Record

- [ ] `post-probe` verbatim (evidence ⊆ response).
- [ ] `../field-notes.md` entry.
- [ ] `classify_solve`/`attempts` filed.
- [ ] `decide.py` if stuck.
