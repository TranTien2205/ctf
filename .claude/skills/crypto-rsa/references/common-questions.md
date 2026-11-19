# Common questions

- **"Just numbers — where to start?"** The `parameter-sheet`, then
  `attack-table.md`. `crypto_attack.py list` for the inventory.
- **"Wiener failed?"** `d<n^0.292` → `boneh-durfee`; `≥` → small-d closed.
- **"e=3 but the root isn't the flag?"** `m³≥n` → `hastad`/`coppersmith`.
- **"Lattice slow?"** `fpylll` absent → pure-python LLL; bound exceeded = fail.
- **"pow!=c but flag-shaped?"** A decoy — `pow` is the gate.
- **"batch-gcd empty?"** `gcd=1` → negative → per-`n` attacks.
- **"inverse fails?"** `gcd(e,phi)>1` → `eth-root`.
- **"partial PEM?"** the non-redacted field → `coppersmith`/`crt`/`factor-from-d`.
- **"hastad <e n's?"** → `coppersmith`/`franklin-reiter`.
- **"a socket?"** printing = numbers; computing = `crypto-symmetric-oracle`.
- **"nothing fires?"** → proper RSA → reclassify.
See `common-questions-deep.md`.
