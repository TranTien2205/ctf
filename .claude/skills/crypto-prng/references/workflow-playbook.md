# Workflow playbook — the procedures by branch

## The LCG playbook

```
3+ outs, m known → lcg-recover
6+ outs, m?      → lcg-unknown-modulus → m → lcg-recover
truncated         → lcg-truncated --low-bits
→ predict → verify → use
```

## The LFSR playbook

```
bits → taps known? → lfsr-predict --count
     → taps? → berlekamp-massey → lfsr-recover → lfsr-predict
→ verify → decrypt/keystream → flag
```

## The MT playbook

```
624 raw words → mt19937-clone → predict_next → verify → flag
<624 → not cloneable → seed-search/re-collect
```

## The xorshift playbook

```
4 outs → xorshift128 --outs --predict → verify → flag
```

## The seed playbook

```
seed=f(small) → bound epoch → random.seed(ts) match → predict → flag
```

## The stuck playbook

```
predict != held → troubleshoot* → falsifiers* → attempts → decide.py
```
