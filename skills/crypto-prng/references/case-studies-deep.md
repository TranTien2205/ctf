# Case studies deep — the narrated solves with the decision points

## Case 1 — the LCG token service (deep)

**Recon**: `GET /token` → `15323`. Repeat → `22011`, `4421`, `9917`. A
stream — each call the next output. The ints look uniform-mod-something.

**Fingerprint**: differences `6688, -17590, 5496` — the magnitudes are
mod-`m` consistent → LCG. Source grep → `MOD = 65536`.

**Gate**: `m` known, ≥3 outputs → `lcg-recover`.

**Solve**:
```bash
python3 tools/crypto_attack.py lcg-recover --outputs 15323,22011,4421 --modulus 65536
# → a=16807? no — the returned a,c
```

**Verify**: `(a*4421 + c) % 65536 == 9917` — the held 4th. Verified.

**Close**: `next = (a*9917 + c) % 65536` → the admin's next token → the
`/redeem` endpoint → `flag{`.

**The decision point**: `m` known → `lcg-recover`, not `lcg-unknown-modulus`.
Reading `MOD` in source saved a step.

## Case 2 — the LFSR stream-ciphered flag (deep)

**Recon**: `ct` is a hex blob + a hint "the flag starts `flag{`". The `flag{`
prefix is known-plaintext → the first keystream bits.

**Fingerprint**: a bitstream → the LFSR family.

**Gate**: ≥2·w bits — the `flag{` prefix gives 40 bits, enough for w≤20.

**Solve**:
```bash
python3 tools/crypto_attack.py berlekamp-massey --keystream-hex <prefix_ct_xor_flag>
# → (w, taps)
python3 tools/crypto_attack.py lfsr-predict --bits <stream> --taps <taps> --width <w> --count <8*len>
# → keystream → ct ⊕ ks → flag{
```

**The decision point**: the known-plaintext prefix is the entry — a bare
`ct` with no `pt` gives no keystream to BM.

## Case 3 — the MT session (deep)

**Recon**: `session_id = str(random.getrandbits(32))`. A private `random`
module — no other callers.

**Gate**: 624 raw words + 1 held back.

**Solve**: 625 calls → `--outputs-file` → `mt19937-clone --count 1` →
`predict == o624` → the admin's id → session hijack → flag.

**The decision point**: `<624` → the clone can't run → the seed-search
branch. The count IS the route.

## Case 4 — the timestamp seed (deep)

**Recon**: `token` has `iat`. The seed is `int(iat)` ± slack.

**Gate**: the window `[iat-5, iat+5]` is bounded.

**Solve**: enumerate `random.Random(ts)` over the window → match → seed →
predict → flag.

**The decision point**: a `time()*1000` ms seed is 1000× the window —
still bounded if `iat` is precise; a `os.urandom` seed is out of class.

## Case 5 — the truncated `java.util.Random` (deep)

**Recon**: `nextInt` leaks `x>>16` (48-bit state, known `a`,`c`,`m`).

**Gate**: `a`,`c`,`m` known + high-bit leak → `lcg-truncated`.

**Solve**: `--low-bits 16` (DROPPED), `--modulus 2^48`, `--a`, `--c` →
the state → the key → decrypt → flag.

**The decision point**: `--low-bits` = 16 dropped, not 32 kept.

## The meta-pattern

Every case pivots on ONE discriminator: `m` known, the known-plaintext,
the 624-count, the bounded seed, the known `a`,`c`,`m`. Find that one
discriminator and the route is decided.
