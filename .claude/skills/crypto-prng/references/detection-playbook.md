# Detection playbook — the branch procedures

## The LCG branch

```
outputs → m known?
  yes → lcg-recover --outputs --modulus
  no  → lcg-unknown-modulus --outputs
truncated (high bits)? → lcg-truncated --low-bits
```

## The LFSR branch

```
bits → taps known?
  yes → lfsr-predict --taps --width --count
  no  → berlekamp-massey → (width, taps) → lfsr-recover → lfsr-predict
```

## The MT branch

```
random outputs → count == 624? → mt19937-clone --outputs
              → count < 624 → cannot clone
```

## The xorshift branch

```
4 outs → xorshift128 --outs --predict
```

## The seed branch

```
seed = f(small)? → bound window → random.seed(ts) match → predict
```

## The fingerprint branch (generator hidden)

```
collect ≥10 → LCG diff/gcd? → LFSR BM? → MT clone test? → seed shape?
→ none → not this class
```

## The close branch

```
predict == held-back → class evidence → flag → impact → post-probe
fail → troubleshoot* → falsifiers* → attempts → decide.py
```
