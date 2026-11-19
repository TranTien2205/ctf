# Glossary deep — every term, defined precisely

## Generator vocabulary

- **PRNG** — pseudorandom number generator; a deterministic finite-state
  machine `state_{i+1}=F(state_i)`, `output_i=G(state_i)`.
- **LCG** — linear congruential generator; `F: x←a·x+c mod m`; `a`
  multiplier, `c` increment, `m` modulus.
- **LFSR** — linear feedback shift register; `F`: shift + `XOR(taps)`;
  `w` width, `taps` feedback positions.
- **MT19937** — Mersenne Twister; 624-word state, `F`=twist (every 624),
  `G`=temper (per output).
- **xorshift128** — `F`: `x^(x<<11)`/rotate/`w^(w>>19)^(t>>8)`; `G`=w.
- **CSPRNG** — cryptographically secure PRNG — `G` one-way; out of scope.
- **seed** — `state_0=init(seed)`; the generator's starting secret.
- **state** — the internal register/array; the attack's target.
- **temper/untemper** — MT's `G` and its inverse.
- **twist** — MT's `F`, the linear state advance.
- **taps** — the LFSR feedback polynomial's set positions.
- **connection polynomial** — the LFSR's `F` as a GF(2) polynomial.

## Output vocabulary

- **consecutive** — `output_i`, `output_{i+1}` adjacent in stream index —
  no other caller between them.
- **raw** — `G(state)` unmodified — not hex/float/`mod n`/`randint`.
- **truncated** — `G = x>>b`; the low `b` bits dropped — `lcg-truncated`.
- **reduced** — `G = x mod n`; the wrapped remainder — a DIFFERENT model.
- **word** — a 32-bit generator output (`getrandbits(32)`).
- **bit** — a 0/1 output (an LFSR's native unit).
- **float** — `random()`/`Math.random` — a `2^53` pair / `128+` output.
- **keystream** — the output stream used to XOR-encrypt in a stream
  cipher.

## Attack vocabulary

- **`a`,`c`,`m`** — the LCG params.
- **`low-bits`** — the DROPPED bit count `b` in `x>>b` (NOT kept).
- **`taps`/`width`** — the LFSR params; `taps` 1-indexed-from-LSB here.
- **`outs`** — comma-separated outputs for `xorshift128`.
- **`outputs`/`--outputs-file`** — the outputs for the dispatched attacks.
- **`count`** — the number of NEXT outputs/bits to emit.
- **`required`** — the `lcg-truncated` count heuristic.
- **linear complexity** — the minimal LFSR width for a stream; BM's key
  output.
- **Hidden-Number Problem (HNP)** — recover `x` from `x>>b` leaks via a
  lattice.

## Evidence vocabulary

- **class evidence** — `predict==held` proves the state.
- **impact evidence** — the flag/forged object.
- **falsifier** — `predict!=held`/`L≈n/2`/`gcd→0/1`.
- **held-back output** — reserved from recovery, used to verify.
- **catalogue class** — a real class nothing here has solved — honest
  status, not local experience.
