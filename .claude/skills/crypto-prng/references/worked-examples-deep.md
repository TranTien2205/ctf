# Worked examples deep — full solves with the reasoning

## Example 1 — an LCG ticket service

**Observation**: `GET /ticket` returns ints, each call the next.
`o = [15323, 22011, 4421, 9917]`, and source names `MOD = 65536`.

**Fingerprint**: differences `6688, -17590, 5496` — affine structure → LCG.

**Attack**: `m` known → `lcg-recover`.

```bash
python3 tools/crypto_attack.py lcg-recover \
  --outputs 15323,22011,4421 --modulus 65536
# returns a, c
```

**Verify**: `predict = (a*4421 + c) % 65536` must equal `9917` — the
held-back 4th. Then predict the next ticket, redeem it → `flag{`.

## Example 2 — unknown-modulus `rand()`

**Observation**: a C service's `rand()` leaks `o = [o0..o7]`, `m` unknown.

**Attack**: `lcg-unknown-modulus`.

```bash
python3 tools/crypto_attack.py lcg-unknown-modulus --outputs o0,...,o7
# gcd(t_{i+1}*t_{i-1} - t_i^2) → m = 2147483648 (2^31) → glibc rand
```

Then `lcg-recover --outputs o0,o1,o2 --modulus 2147483648` → `a,c` →
predict.

## Example 3 — `java.util.Random` keygen

**Observation**: a keygen leaks `key >> 16` per call (48-bit `java.util.Random`).

**Attack**: `lcg-truncated` with the KNOWN `m=2^48, a=0x5DEECE66D, c=0xB`,
`low-bits=16` (the DROPPED bits).

```bash
python3 tools/crypto_attack.py lcg-truncated \
  --outputs <leaks> --modulus 281474976710656 \
  --a 25214903917 --c 11 --low-bits 16
```

**Verify**: the recovered state's `>>16` matches a held-back leak.

## Example 4 — LFSR stream cipher

**Observation**: `ct = flag ⊕ ks`, `flag` starts `flag{` → known prefix.

**Attack**:

```bash
python3 tools/crypto_attack.py berlekamp-massey --keystream-hex <ks_prefix>
# → (width, taps), say w=16
python3 tools/crypto_attack.py lfsr-predict \
  --bits <stream> --taps <taps> --width 16 --count <8*flag_len>
# → the keystream → ct ⊕ ks → flag{
```

## Example 5 — MT session prediction

**Observation**: `session_id = str(random.getrandbits(32))`, a private
`random` module.

**Attack**: collect 625 calls; `o0..o623` recover, `o624` held back.

```bash
python3 tools/crypto_attack.py mt19937-clone --outputs-file outs.txt --count 1
# predict_next == o624 → verified → predict_next = the admin's id → hijack → flag
```

## Example 6 — timestamp-seeded token

**Observation**: `token = str(random.Random(int(time())).getrandbits(32))`,
`iat` in the token.

**Attack**: seed-search.

```python
import random
for ts in range(iat-5, iat+5):
    if random.Random(ts).getrandbits(32) == token: seed = ts
# predict the next with random.Random(ts).getrandbits(32)
```

## Example 7 — xorshift cookie

**Observation**: 4 consecutive `xorshift128` cookie values.

**Attack**: `python3 tools/crypto/xorshift128.py --outs o0,o1,o2,o3 --predict 1`
→ the 5th cookie → `flag{`.

## The meta-lesson

Every example is: name the generator, meet the count, normalize to raw,
the matching attack, `predict==held`, use, flag. The count gate and the
normalization are where every solve actually lives.
