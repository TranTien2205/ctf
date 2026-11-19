# Detection playbook deep — the branch procedures, annotated

## The LCG branch — annotated

```
raw ints + 'a·x+c' structure?
  m known  → lcg-recover --outputs --modulus
             └ the closed form — a,c from one inverse
  m?       → lcg-unknown-modulus --outputs
             └ the gcd trick — >=6 outs
  x>>b leak+params → lcg-truncated --low-bits
             └ the HNP lattice
```

The `m`-known read is the discriminator — `MOD`/`modulus`/`2^31`/`2^48`
in source → `lcg-recover` skips the gcd.

## The LFSR branch — annotated

```
bitstream + taps?   → lfsr-predict --taps --width --count
bitstream + taps?   → berlekamp-massey → (w,taps) → lfsr-recover → predict
```

The `taps`-known read is the discriminator. A `flag{` known-plaintext
prefix yields the entry keystream.

## The MT branch — annotated

```
624 raw getrandbits(32) → mt19937-clone --outputs
<624 → not cloneable → seed-search / re-collect
```

The 624 count is the hard gate — the clone can't run below it.

## The xorshift branch — annotated

```
4 consecutive words → xorshift128.py --outs --predict
```

The variant is the discriminator — `xorshift128` vs `128+`/`64*`.

## The seed branch — annotated

```
seed=f(small) + bounded window → enumerate → match → predict
```

The window bound is the discriminator — `iat`/`created` collapses the
seed space; `os.urandom`/`secrets` is out.

## The close branch — annotated

```
predict == held → use → flag → post-probe/pre-flag → record
predict != held → troubleshoot → falsifier → attempts → decide.py
```

`predict==held` is the only accept; `predict!=held` is the falsifier —
never chain past it.
