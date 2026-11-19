# Workflow playbook deep — the branches, annotated

## The LCG playbook — annotated

```
raw ints + 'x_{i+1}=a·x+c' structure?
  m known  → lcg-recover --outputs --modulus
             └ the closed form; gcd(x1-x0,m)=1 the only obstruction
  m?       → lcg-unknown-modulus --outputs
             └ the gcd trick; >=6 outs; gcd→0/1 = not-affine falsifier
  x>>b leak + a,c,m → lcg-truncated --low-bits b
             └ HNP lattice; --low-bits is DROPPED
→ predict_next == held? → use → flag
```

**The decision is `m` known.** Read source for `MOD`/`modulus`/`2^31`/
`2^48` first — it saves a step.

## The LFSR playbook — annotated

```
bitstream + taps known? → lfsr-predict --taps --width --count
bitstream + taps?      → berlekamp-massey --bits → (w,taps)
                       → lfsr-recover --bits --width → register
                       → lfsr-predict --taps --width --count → future
→ ct ⊕ keystream → flag
```

**The decision is `taps` known.** A `flag{`/`CTF{` known-plaintext prefix
yields the entry keystream — the common stream-cipher shape.

## The MT playbook — annotated

```
624 consecutive raw getrandbits(32) → mt19937-clone --outputs
<624 → NOT cloneable → seed-search / re-collect
→ predict_next == held? → the admin's session id → hijack → flag
```

**The decision is the count.** 624 is the hard gate — the clone can't run
below it. A reseeding oracle or shared `random` module forces the
seed-search branch.

## The xorshift playbook — annotated

```
4 consecutive words → xorshift128.py --outs --predict
→ predict == held? → flag
```

**The decision is the variant.** `xorshift128` vs `128+` (Math.random) vs
`64*` — fingerprint before the tool.

## The seed playbook — annotated

```
seed = f(small)? + bounded window → enumerate → match → predict → flag
```

**The decision is the window bound.** `iat`/`created`/`time` collapses
`[issue-slack, now]`; an unbounded/`urandom` seed is out of class.

## The stuck playbook — annotated

```
predict != held
  → the convention (low-bits/taps)
  → the variant (mt_rand/128+/java.util.Random/glibc)
  → the normalization (float/mod/randint)
  → the alignment (gap/reseed)
  → the count (<floor)
  → still fail → falsifier → attempts → decide.py rung
```

Change the MECHANISM, not the same model's flag — a 6th variant of a
falsified model is the anti-pattern.
