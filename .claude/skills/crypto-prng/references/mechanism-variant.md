# Mechanism variant — the (F,G) pairs as code

## The model

```python
class Generator:
    state: int
    def step(self):           # F
        self.state = F(self.state)
    def output(self):         # G
        self.step()
        return G(self.state)
```

Every attack inverts `G` to recover `state`, then replays `F`.

## LCG as code

```python
def F(x): return (a*x + c) % m
def G(x): return x                     # raw
def G(x): return x >> b                # truncated
def G(x): return x % n                 # reduced — different problem
```

- `lcg-recover`: solve `x1-x0` vs `x2-x1` for `a` — one inverse.
- `lcg-unknown-modulus`: `gcd(t_{i+1}t_{i-1}-t_i^2)` kills `m`.
- `lcg-truncated`: `G=x>>b` → `x_i = h_i·2^b + l_i`, `l_i<2^b` → lattice.

## LFSR as code

```python
def F(reg):
    new = xor_bits(reg, taps)          # feedback
    return ((reg << 1) | new) & mask   # shift in
def G(reg): return reg & 1             # or reg >> (w-1), the end bit
```

- `lfsr-recover`: the last `w` `G(reg)` outputs ARE the register.
- `berlekamp-massey`: infer `taps` from `2w` `G` outputs.

## MT19937 as code

```python
def F(state):     # twist, every 624 outputs
    for i in range(624): state[i] = twist(state, i)
def G(y):         # temper — invertible
    y ^= y>>11; y ^= (y<<7)&B; y ^= (y<<15)&C; y ^= y>>18
    return y
def untemper(y):  # invert each step
    ...
```

- `mt19937-clone`: `state[i] = untemper(o_i)` for 624 `o_i`.

## xorshift128 as code

```python
def F(x,y,z,w):
    t = x ^ (x<<11)
    return y, z, w, w ^ (w>>19) ^ t ^ (t>>8)
def G(x,y,z,w): return w
```

- `xorshift128`: 4 `G`s = `w` history = the state.

## The seed as code

```python
state_0 = init(seed)   # init_genrand / the LCG seed / the LFSR load
for s in seed_window:
    if Generator(s).output() == observed: state_0 = init(s)
```

## The post-processing wrapper

```python
randint = a + (G(state) * (b-a)) // m
choice  = seq[G(state) % len(seq)]
random  = (G(state1)<<26 | G(state2)>>5) / 2**53   # two words per float
```

`G` is wrapped — recover `G(state)` first, or the model is wrong.

## The combiner — out of scope

```python
def G(r1, r2, r3): return f(r1, r2, r3)   # nonlinear f
```

`f` nonlinear → BM complexity ≈ product → the falsifier → correlation
attack, not this module.
