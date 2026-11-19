# Workflow variant 3 — the procedures by result shape

## The scalar-return procedures

- `ecdsa-nonce-reuse`/`hnp-*`/`pohlig-hellman`/`bsgs`/`smart`/`singular`
  all return a scalar → verify `x·G == Q`/`pow == h` → the flag step.

## The oracle-response procedures

- invalid curve: response is `d·P'` → `d mod ord_i` per curve → CRT → `d`.

## The lattice-return procedures

- `hnp`/`hnp-ecdsa` return a vector → `d` extracted → verify.

## The dead-end procedures

- `smoothness` largest > 2⁴⁰ → not PH.
- `bsgs` no match → `h ∈ <g>` re-check.
- `hnp` verify-fail → `z`/`ord`/`bound` re-check.

## The flag procedures

- `x` → decrypt/decrypt-DH → `flag{`.
- `d` → forge → `flag{`.
- Scalar itself → the flag when it's the answer (rare — usually a step).
