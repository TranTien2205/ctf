# Theory catalogue — every theorem, its bound, its file

## The factoring theorems

- **Fermat** — `n=a²-b²`, `|p-q|` small → `fermat.md`.
- **Pollard p-1** — `p-1` `B`-smooth → `pollard-pm1.md`.
- **batch-gcd** — shared prime → `batch-gcd.md`.
- **trial/ECM/QS/NFS** — the general factoring methods; not this class's tools.

## The small-d theorems

- **Wiener** — `d<n^0.25`, CF → `wiener.md`.
- **Boneh-Durfee** — `d<n^0.292`, bivariate LLL → `boneh-durfee.md`.

## The small-root theorems

- **Coppersmith univariate** — `f(x)≡0 mod p`, `|x|<n^(β²/d)` → `coppersmith.md`.
- **Coppersmith bivariate** — small `d` → `boneh-durfee.md`.
- **partial-message** — `f(x)≡0 mod n`, `|x|<n^(1/e)` → `coppersmith.md`.

## The broadcast / relation theorems

- **Håstad** — same `m`, `e` moduli → `hastad.md`.
- **Franklin-Reiter** — `m2=a·m1+b` → `franklin-reiter.md`.
- **common-modulus** — `gcd(e1,e2)=1` → `common-modulus.md`.
- **CRT** — residues → `crt.md`.
- **Bellcore** — a fault → `crt.md`.

## The algebraic theorems

- **factor-from-d** — `ed-1` splits `n` → `factor-from-d.md`.
- **eth-root** — `gcd(e,phi)>1` → `crt.md`/`factor-from-d.md`.
- **Bezout** — `a·e1+b·e2=1` → `common-modulus.md`.
- **CF / Legendre** — `k/d` a convergent → `wiener.md`.

## The verify theorem

`pow(m,e,n)==c` ⇔ `m` is the plaintext — the RSA identity itself.
