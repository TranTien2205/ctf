# Payload families — the input, by the object it is

## Family 1 — the integers (the common case)

`n`,`e`,`c`,`p`,`q`,`d`,`phi`,`dp`,`dq`,`qInv`,`a`,`b`,`B`,`m` — the RSA values.
Pass them as `--n`, `--e`, … to `crypto_attack.py`. Build them on the
parameter-sheet; the attack is arithmetic, not a string.

## Family 2 — the lists

`--moduli n1 n2 n3 ...` for `batch-gcd`; `--pairs c1 c2 ... --moduli n1 n2
...` for `hastad`; `--residues r1 r2 ... --moduli p1 p2 ...` for `crt`. The
length rules: `hastad` needs `count ≥ e`; `crt` needs `∏pi > m`.

## Family 3 — the relations

`franklin-reiter` takes `--a --b` for `m2 = a·m1+b`. `coppersmith-core` takes a
polynomial `--a`. `common-modulus` takes `--e1 --c1 --e2 --c2`. The relation is
the payload.

## Family 4 — the bounds

`--b` for `pollard-pm1`; `--bits` for `coppersmith`; `m`/`t` (implicit)
for `boneh-durfee`. The bound is a parameter — too small misses; too large is
slow.

## Family 5 — the leaks

`--d`, `--phi`, `--dp`, `--dq`, `--qInv`, `--p`, `--q`, `--known`. The
leaked value is the input — `factor-from-d`, `crt`, `eth-root`, `rsa-decrypt`,
`coppersmith-*`.

## Family 6 — the key/cert

A `.pem`/`.der`/`crt` is parsed with `RSA.importKey` — `n`,`e` public, or
`n`,`e`,`d`,`p`,`q`,`dp`,`dq`,`qInv` private. The file is the payload; the tool
flags take the extracted integers.

## The verify

The only payload that *proves* anything: `pow(m,e,n)==c` / `p*q==n`.
