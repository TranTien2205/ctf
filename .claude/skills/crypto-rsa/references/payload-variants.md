# Payload variants — the same attack, different flag layouts

## fermat variants
```bash
crypto_attack.py fermat --n <n>                      # default
crypto_attack.py fermat --n <n> --max-iters <K>       # bound the climb
```

## batch-gcd variants
```bash
crypto_attack.py batch-gcd --moduli <n1> <n2> ...    # pairwise
# or a driver loop for a large list
```

## common-modulus variants
```bash
crypto_attack.py common-modulus --n <n> --e1 3 --e2 17 --c1 <c1> --c2 <c2>
```

## wiener / boneh-durfee variants
```bash
crypto_attack.py wiener --n <n> --e <e>
crypto_attack.py boneh-durfee --n <n> --e <e>
crypto_attack.py boneh-durfee-escalate --n <n> --e <e> --m 4 --t 3
```

## coppersmith variants
```bash
crypto_attack.py coppersmith-high-bits --n <n> --known <a> --bits <b>
crypto_attack.py coppersmith-core --n <n> --a "x^2 + 3x + 2"   # the small root
```

## small-e / hastad variants
```bash
crypto_attack.py small-e-root --c <c> --e 3 --n <n>
crypto_attack.py nth-root --x <x> --n <n> --n <n>
crypto_attack.py hastad --pairs c1 c2 c3 --moduli n1 n2 n3 --e 3
```

## pollard-pm1 variants
```bash
crypto_attack.py pollard-pm1 --n <n> --b 100000
crypto_attack.py pollard-pm1 --n <n> --b <larger>   # raise B if gcd=1
```

## crt variants
```bash
crypto_attack.py crt --residues "<r1>,<r2>" --moduli "<p1>,<p2>"
crypto_attack.py # crt --residues/--moduli only — Bellcore/dp are manual (gcd / dp-loop), not tool flags
crypto_attack.py # crt --residues/--moduli only — dp/dq/qInv recovery is manual
```

## factor-from-d / rsa-decrypt / eth-root variants
```bash
crypto_attack.py factor-from-d --n <n> --e <e> --d <d>
crypto_attack.py rsa-decrypt --n <n> --e <e> --c <c> --p <p> --q <q>
crypto_attack.py eth-root --c <c> --e <e> --factors "<p>,<q>"
```

## franklin-reiter variants
```bash
franklin-reiter --n <n> --e 3 --a <a> --b <b> --c1 <c1> --c2 <c2>
```

## The rule

`<id> --help` is the contract — the flag names and the bound line differ per
attack. Never guess a flag.
