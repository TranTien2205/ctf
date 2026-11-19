# Troubleshoot deep — every stall, its cause, its fix

## "The script ran but printed nothing / an error"

- Read the traceback — a `ValueError`/`ZeroDivisionError` is often the bound:
  `inverse` failing → `gcd(e,phi)>1` → `eth-root`, not a crash.
- `crypto_attack.py <id> --help` for the exact flag names — they differ per id.
- The args are *integers* — pass `0x…` or decimal; a string flag fails.

## "Wiener returned nothing"

`d ≥ n^0.25` — out of Wiener's bound. Escalate: `boneh-durfee`, then
`boneh-durfee-escalate` (`m`,`t` up). If `d ≥ n^0.292` → small-d closed, record
the negative.

## "Boneh-Durfee is slow / hangs"

`fpylll` is absent → pure-python LLL. `tools/crypto/` is stdlib-only by design.
`crypto_attack.py list` reports `lll_backend`. It is *slow*, not broken — give
it the budget. If the bound was exceeded it is failing, not slow — check
`d<n^0.292` before assuming.

## "Coppersmith found no root"

- The unknown window `< n^0.25` — out of bound. Measure the leak again; a bigger
  known window is the only fix.
- `fpylll` absent → the pure-python LLL may be weaker at the edge of the bound.
- The polynomial / `a` was wrong — recheck the leak layout.

## "batch-gcd all gcd=1"

No prime collision — the RNG was fine. Record the negative; route per-`n` to the
single-modulus attacks (`fermat`, `wiener`, …). The *count* is not the bug.

## "Hastad root isn't the flag"

- `<e` ciphertexts → `∏ni<m^e` → the root isn't `m`. Route `coppersmith` or
  `franklin-reiter`.
- A pad was applied → `m` differs per `n` → `hastad` dead; route `coppersmith`
  partial-message.
- The root is a padded block → strip `\x00\x02<pad>\x00`.

## "pow(m,e,n)!=c"

- A decoy — a flag-shaped string that fails `pow` is a candidate.
- The wrong `eth-root` candidate → try the others.
- A pad → `pow` held on the padded block; strip for the flag.
- The recovered `d`/`phi` was wrong → recheck the algebra.

## "fermat climbs forever"

`|p-q|` too large — `a` walks `O(|p-q|)`. Bound it (`--max-iters`) and route to
`pollard-pm1`, `coppersmith`, or a leak.

## "pollard-pm1 gcd=1 for B"

`p-1` has a factor `>B` — raise `B`. If `B` already large → `p-1` not smooth →
record the negative.

## "inverse(e,phi) fails"

`gcd(e,phi)>1` → `eth-root` — the gcd candidates; `pow`+format picks the true
root.

## "The PEM won't import"

- A `.der` (binary) vs `.pem` (base64) mismatch — `RSA.importKey` handles both
  if the bytes are right; check `openssl asn1parse`.
- A *certificate* (`.crt`) — `openssl x509 -pubkey -noout -in c.crt` for the key.
- An *encrypted* private key — needs the passphrase; the redacted fields are the
  attack surface instead.

## "Nothing in attack-table.md fires"

Proper RSA → the class falsifier. The bug is in the protocol — a padding oracle,
a signature forgery, a side channel, or a `crypto-*` neighbour class. Route via
`class-boundary.md`.
