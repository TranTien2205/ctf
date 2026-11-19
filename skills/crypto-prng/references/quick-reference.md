# Quick reference — the one-page card

## The group

```
gen ∈ {lcg, lfsr, mt19937, xorshift128, seed}
outputs: consecutive, raw ints
```

## The gates

```
lcg:  m known → lcg-recover --outputs --modulus
      m? → lcg-unknown-modulus --outputs
      truncated → lcg-truncated --low-bits
lfsr: taps? → lfsr-predict | taps? → berlekamp-massey → lfsr-recover
mt:   624 words → mt19937-clone --outputs
xor:  4 words → xorshift128 --outs --predict
seed: bounded window → enumerate
```

## The counts

```
lcg-recover 3 · lcg-unknown-modulus 6 · lcg-truncated ~required
berlekamp-massey 2·w bits · mt19937-clone 624 · xorshift128 4
```

## The verify

```
predict_next == held_back     # the only accept
```

## The flag

```
flag{ | CTF{ — from the forged/decrypted object, not the state
```

## The record

```
post-probe → field-notes → classify_solve/attempts → decide.py
```

## The honest status

Catalogue — no local chains; corpus is the field procedure.
