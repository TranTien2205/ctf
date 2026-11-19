# Payload catalogue — the invocations by category

## The single-modulus

`fermat --n [--max-iters]` · `wiener --n --e` · `boneh-durfee --n --e
[--delta --m --t]` · `boneh-durfee-escalate --n --e [--m --t]` ·
`small-e-root --n --e --c [--max-k]` · `nth-root --x --n` ·
`pollard-pm1 --n [--b]` · `coppersmith-high-bits --n --known --bits [--p-bits
--m --t]` · `coppersmith-core --n --a --X [--m --t]`.

## The multi-modulus

`batch-gcd --moduli n1 n2 ...` / `--file` · `hastad --pairs "n1,c1;n2,c2" --e` /
`--n --c` · `common-modulus --n --e1 --c1 --e2 --c2` · `crt --residues
"r1,r2" --moduli "p1,p2"`.

## The terminal

`factor-from-d --n --e [--d] [--phi]` · `rsa-decrypt --n --e --c --p --q` ·
`eth-root --c --e --factors "<p>,<q>"`.

## The manual

`tools/crypto/franklin_reiter.py` (`franklin-reiter`) · `crt` Bellcore `gcd` ·
`crt` `dp`/`qInv` loop.

## The flags

`crypto_attack.py <id> --help` — the real flags. `--json`, `--in <file>` are
global.
