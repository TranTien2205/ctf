# Payload dictionary full — every id, the flags, the shape, the bound

## Single-modulus — the factors

### `fermat`
`crypto_attack.py fermat --n <n> [--max-iters <K>]`
`|p-q|` small → `p,q`. The `a` walk `O(|p-q|)`; `--max-iters` bounds it.

### `pollard-pm1`
`crypto_attack.py pollard-pm1 --n <n> [--b <B>]`
`p-1` `B`-smooth → `p`. `gcd=1` → raise `B` or closed.

### `coppersmith-high-bits`
`crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits <b>
[--p-bits <pb>] [--m] [--t]`
`p` = `a` + `x`, `|x| < n^0.25` → `p`. `--p-bits` the factor size hint.

### `coppersmith-core`
`crypto_attack.py coppersmith-core --n <n> --a <a> --X <bound> [--m] [--t]`
a centred guess `a` within `n^0.25` → `p`.

## Single-modulus — small d

### `wiener`
`crypto_attack.py wiener --n <n> --e <e>`
`d < n^0.25` → `d`. `e≈n` is the tell.

### `boneh-durfee`
`crypto_attack.py boneh-durfee --n <n> --e <e> [--delta] [--m] [--t]`
`d < n^0.292` → `d`/`p,q`. LLL.

### `boneh-durfee-escalate`
`crypto_attack.py boneh-durfee-escalate --n <n> --e <e> [--m] [--t]`
raise `m`,`t` to approach `n^0.292`.

## Single-modulus — wrap

### `small-e-root`
`crypto_attack.py small-e-root --n <n> --e <e> --c <c> [--max-k <k>]`
`m^e < n` → `m`. `--max-k` the wrap-multiplicity bound.

### `nth-root`
`crypto_attack.py nth-root --x <x> --n <n>`
`x = m^n` exact → `m`. The general root.

## Multi-modulus

### `batch-gcd`
`crypto_attack.py batch-gcd --moduli n1 n2 ...` / `--file <f>`
a shared `p` → `(i,j,p)`.

### `hastad`
`crypto_attack.py hastad --pairs "n1,c1;n2,c2;..." --e <e>` / `--n --c`
`≥e` coprime `n`, same `m`, `∏n>m^e` → `m`.

### `common-modulus`
`crypto_attack.py common-modulus --n <n> --e1 --c1 --e2 --c2`
`gcd(e1,e2)=1` → `m`.

### `crt`
`crypto_attack.py crt --residues "r1,r2,..." --moduli "p1,p2,..."`
`m mod pi`, `∏pi>m` → `m`.

## Terminal

### `factor-from-d`
`crypto_attack.py factor-from-d --n <n> --e <e> [--d] [--phi]`
`d`/`phi` held → `p,q`.

### `rsa-decrypt`
`crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>`
`p`,`q` held → `m`.

### `eth-root`
`crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"`
`gcd(e,phi)>1` → the `g` candidates.

## Manual

`franklin-reiter` → `tools/crypto/franklin_reiter.py` · `crt` Bellcore `gcd` ·
`crt` `dp`/`qInv` loop.

## Global flags

`--json` compact output · `--in <file>` a JSON param object (`-` = stdin).
