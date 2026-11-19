# First hour — the 0→60-minute plan

## 0–5 min: read the handout

- Note the group: curve name, `p`, `a`, `b`, `G`, `n`.
- Inventory signatures `(r, s, z)` if present.
- Note any service/oracle shape.

## 5–10 min: the cheap gates

- Scan `r`s for duplicates.
- `crypto_attack.py smoothness --n <order>`.
- Custom curve: `#E == p`? `Δ == 0`?
- `cipher_id`-style check not needed — it's math, not text.

## 10–25 min: the solve

- `ecdsa-nonce-reuse` / `hnp-ecdsa` / `pohlig-hellman` / `bsgs` /
  `smart_attack` / `singular_ec` / invalid-curve — per `cipher-identification.md`.
- Prepare `--sigs` JSON carefully — the format trips the most.

## 25–30 min: verify

- `x·G == Q` or `g^x == h` — non-negotiable.
- Decrypt / forge → `flag{…}`.

## 30–45 min: record

- `post-probe` with the verbatim output.
- Fail → `knowledge/attempts/` falsifier.
- Stuck → `decide.py` escalation rungs.

## The budget

5 probes / 15 min per mechanism, 25 / 45 total — `decide.py` enforces it,
not your discipline.
