# Anti-patterns — the shapes that waste the budget

## The variant loop

- Trying 20 `--nonce-bound` values hoping one hits → the bound comes from the
  challenge statement ("128-bit nonce", "timestamp k"), not brute force.
  When it doesn't say: infer from the observed `k` range in oracle responses.
- Re-running `hnp-ecdsa` with the same sigs and bound expecting a different
  `d` → LLL is deterministic; same input, same lattice.

## The wrong-family loop

- `bsgs` on a 256-bit order → the table never builds; if you wanted a small
  solve, the challenge is telling you it's a *defect curve* (smart/singular/
  invalid), not generic dlog.
- `pohlig-hellman` on a safe-prime order → PH needs smooth; a 2q order is
  designed to resist it.

## The single-signature loop

- Extracting `r`, `s`, `z` from one signature and rotating attacks — one
  signature has zero nonce information; gather more or use the oracle.

## The curve-fixation

- Solving ECDLP directly on a singular curve — map via `singular_ec` first.
- Using `p` where `n` belongs — `order` args are always `n`.

## The claim-before-verify

- Recording a scalar before `x·G == Q` — the verify is the finish line.
- Treating `crypto_attack.py` output as final — it reports candidates;
  the verify proves them.
