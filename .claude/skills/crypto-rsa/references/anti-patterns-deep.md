# Anti-patterns deep — the deterministic losses, annotated

## "e=3 means small-e"

`e=3` is weak only when `m³<n` — a real flag usually wraps. Run the read:
`m³<n` → `small-e-root`; `≥e` n's → `hastad`; a pad → dead.

## "A large e is a bug"

A large `e` is the *opposite* tell — `e=inverse(d,phi)` for a small `d` ≈ `n`.
`e≈n` → `wiener`/`boneh-durfee` (small `d`), not an `e`-attack.

## "Two n's means batch-gcd"

The `n` *count* is not the bug — a *collision* (`gcd>1`) is. All `gcd=1` → no
shared prime → a negative; route per-`n` elsewhere.

## "Wiener didn't work, try again"

Wiener is deterministic for `d<n^0.25` — a no-find is a bound, not a failure.
`d≥n^0.25` → `boneh-durfee`; `d≥n^0.292` → small-d closed.

## "Fermat takes forever, retry"

The `a` walk is `O(|p-q|)` — bounded by `--max-iters`. Past it, `|p-q|` is too
large → dead; route `pollard-pm1`/a leak. Not a retry.

## "Try a bigger coppersmith window"

The window is `n^0.25` (factor)/`n^(1/e)` (message) — a theorem. A smaller leak
→ dead; a larger leak → route to the right Coppersmith.

## "The plaintext is m — flag it"

`m` is a candidate until `pow(m,e,n)==c`. The pad may need stripping; the flag
is the *bytes* that `pow` confirms, not `m` alone.

## "Pollard p-1 failed, n is strong"

`p-1` smooth is one weakness — `gcd=1` at `B` means the largest `p-1` factor
exceeds `B`. Raise `B` or route — the failure is a bound, not a verdict on `n`.

## "Factor it with fermat"

`fermat` needs `|p-q|` small — a balanced `p`,`q` with a large gap isn't close.
Check the keygen tell (`next_prime`,`p+k`) before the walk.

## "Pow is enough — the m is a flag"

`pow(m,e,n)==c` proves `m` is the decryption — but the *bytes* must be the
flag. A `m` that re-encrypts but reads garbage is a wrong root (`eth-root`) or
a decoy.
