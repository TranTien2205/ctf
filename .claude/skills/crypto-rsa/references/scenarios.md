# Scenarios — the challenge presentations, and the route for each

## "Here is an RSA-encrypted flag"

`n`,`e`,`c` in a `.txt`. Fill the sheet. `e`=65537 → read the keygen — `p`,`q`
close? `d` small? a leak? The bug is in the generator, not `e`.

## "We generated 1000 public keys — some share a prime"

A `.json` of `n`,`e`. `batch-gcd` — pairwise `gcd`, a collision → `p`,`q` →
`rsa-decrypt` that `n`'s `c`.

## "The same secret was sent to three recipients"

`e`=3, three `n`,`c`. `hastad` — CRT + cube root → `m`. If only two →
`franklin-reiter` or `coppersmith`.

## "Our private key got partially leaked"

`priv.pem` with fields redacted. `p`-bits → `coppersmith`; `dp`,`dq`,`qInv` →
`crt`; `d`/`phi` → `factor-from-d`. Read which field is *not* redacted.

## "Small e is faster"

`e`=3, `m` short → `small-e-root`. `e`=3, `m` wrapped → `hastad`/`coppersmith`.
`e`=3, `m2=a·m1+b` → `franklin-reiter`.

## "We use a small private exponent for speed"

`e`≈`n` → `wiener` (`d<n^0.25`) then `boneh-durfee` (`d<n^0.292`).

## "Two parties encrypt the same message with different e, same n"

`common-modulus` — Bezout.

## "Our primes are safe — p is random"

`p-1` smooth → `pollard-pm1`. Or `p` reused → `batch-gcd`. Or `p`,`q` close →
`fermat`. The keygen line names it.

## "A signing device sometimes returns a bad signature"

correct + faulty `sig` of the same `m` → `crt` Bellcore — `gcd(s'^e-m,n)=q`.

## "Decrypt this — we accidentally stored d too"

`d`/`phi`/`p`,`q` in the handout → `factor-from-d`/`rsa-decrypt`.

## "We split the secret across primes"

residues `mod pi`, `∏pi>m` → `crt` reconstruction.

## "nc host port — prints n,e,c"

Transport — the numbers. Fill the sheet, the discriminator routes. If it
re-encrypts → `crypto-symmetric-oracle`.

## "This RSA is unusual"

`n=p²`, `n` prime, `n=p·q·r` — degenerate `phi`. `gcd(e,phi)>1` → `eth-root`.
A multiprime → `phi=∏(pi-1)`.
