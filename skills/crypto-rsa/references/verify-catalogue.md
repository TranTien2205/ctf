# Verify catalogue — the proof per recovery, indexed

## The recovery types → the check

| Recovery | The gate | The chain |
|---|---|---|
| `m` | `pow(m,e,n)==c` | direct — `m` is `c` decrypted |
| `p`,`q` | `p*q==n` | → `phi` → `d` → `m` → `pow` |
| `d` | `pow(c,d,n)==m` | → `pow(m,e,n)==c` |
| `phi` | `n-phi+1==p+q` | → `d` → `m` → `pow` |
| `p` (one) | `1<p<n`,`p|n` | → `q=n/p` → `phi` → `d` → `m` → `pow` |
| `m_i` (`eth-root`) | `pow(m_i,e,n)==c` + format | the true root among `g` |

## The read order

1. `pow(m,e,n)==c` — the cryptographic confirm (asserts `m` unique).
2. `long_to_bytes(m)` — the content (strip a pad; the flag bytes must appear).
3. `p*q==n` — the factor confirm (for a factor recovery).

## The decoy

A flag-shaped `m` that fails `pow` is a decoy; a `p*q` that fails `==n` is a
false split; a `d` that doesn't decrypt is wrong. The gate is the identity —
run it.

## The record

`pow`/`p*q` → `hooks.py post-probe --verdict confirms` → `classify_solve.py
--chain <id>` after a solve.
