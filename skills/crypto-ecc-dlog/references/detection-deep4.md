# Detection deep 4 — the reads by what's missing, expanded

## Missing `n`/`ord` — expanded

- Named curve → the published `n`/`ord` applies.
- Custom curve → `#E`/`ord(G)` must be counted (small `p`) — or the
  defect intent is the point.
- `h = g^x` → `ord(g)` derived from `p` (`p-1` for a generator).

## Missing bound — expanded

- No `k` bound stated → `hnp-ecdsa` has no `--nonce-*` → only reuse.
- No `x` bound → `bsgs` gets `--order ord` — feasible iff `ord ≤ 2⁴⁴`.

## Missing `Q`/`h` — expanded

- `x`/`d` is the answer → flag IS the proof, not `x·G == Q`.
- `Q`/`h` absent but `x`/`d` verifiable another way → use it.

## Missing a clean discriminator — expanded

- `r` equal + `k` bound stated → prefer `ecdsa-nonce-reuse` (closed form).
- `ord` smooth + `x` bounded → `pohlig-hellman` usually wins.
- `Δ == 0` + `P` unvalidated → `singular_ec` first (cheaper solve).

## Missing selftests — expanded

`tools/crypto/*.py --selftest` proves the module offline before the real
params go in.
