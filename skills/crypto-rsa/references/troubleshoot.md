# Troubleshoot — the stalls

- **`inverse`/`ZeroDivisionError`** → `gcd(e,phi)>1` → `eth-root`.
- **`wiener` nothing** → `d≥n^0.25` → `boneh-durfee`.
- **`boneh-durfee` slow** → pure-python LLL (`fpylll` absent) — budget it.
- **`coppersmith` no root** → window `<n^0.25` or wrong `a`/`f`.
- **`batch-gcd` all gcd=1** → no collision → per-`n` attacks.
- **`hastad` root ≠ flag** → `<e` n's or a pad → `coppersmith`/`franklin-reiter`.
- **`pow!=c`** → decoy / wrong root / a pad to strip.
- **`fermat` climbs** → `|p-q|` too large → `pollard-pm1`/a leak.
- **PEM won't import** → `.der` vs `.pem`, a cert, an encrypted key.
- **nothing fires** → proper RSA → `class-boundary.md` — the bug is the protocol.
See `troubleshoot-deep.md`.
