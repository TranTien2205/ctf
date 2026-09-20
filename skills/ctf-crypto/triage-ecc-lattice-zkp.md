# Elliptic curves, lattices and proof systems

The three families that need their parameters collected before any attack is
named. Depth in `ecc-attacks.md`, `lattice-and-lwe.md`, `zkp-and-advanced.md`.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Elliptic Curve Attacks

- **Small subgroup:** Check curve order for small factors; Pohlig-Hellman + CRT
- **Invalid curve:** Send points on weaker curves if validation missing
- **Singular curves:** Discriminant = 0; DLP maps to additive/multiplicative group
- **Smart's attack:** Anomalous curves (order = p); p-adic lift solves DLP in O(1)
- **Baby-step giant-step (BSGS):** General DLP in O(sqrt(n)) time/space. Combined with Pohlig-Hellman for smooth-order groups (all factors of `p-1` or curve order are small). Sage: `discrete_log(Mod(h,p), Mod(g,p))`. See [advanced-math.md](advanced-math.md#baby-step-giant-step-for-general-dlp).
- **Fault injection:** Compare correct vs faulty output; recover key bit-by-bit
- **Clock group (x^2+y^2=1):** Order = p+1 (not p-1!); Pohlig-Hellman when p+1 is smooth
- **Isogenies:** Graph traversal via modular polynomials; pathfinding via LCA
- **ECDSA nonce reuse:** Same `r` in two signatures leaks nonce `k` and private key `d` via modular arithmetic. Check for repeated `r` values
- **Braid group DH:** Alexander polynomial is multiplicative under braid concatenation — Eve computes shared secret from public keys. See [exotic-crypto.md](exotic-crypto.md#braid-group-dh--alexander-polynomial-multiplicativity-dicectf-2026)
- **Ed25519 torsion side channel:** Cofactor h=8 leaks secret scalar bits when key derivation uses `key = master * uid mod l`; query powers of 2, check y-coordinate consistency
- **Tropical semiring residuation:** Tropical (min-plus) DH is broken — residual `b* = max(Mb[i] - M[i][j])` recovers shared secret directly from public matrices
- **FPE Feistel brute-force:** Format-preserving encryption with 16-bit round key is brute-forceable; remaining affine GF(2) mixing layer solved via Gaussian elimination. See [exotic-crypto.md](exotic-crypto.md#format-preserving-encryption-feistel-brute-force-bsidessf-2026)
- **Icosahedral symmetry cipher:** Dodecahedron face permutations form order-120 group; build lookup table of all permutations via API probing, match visible face patterns. See [exotic-crypto.md](exotic-crypto.md#icosahedral-symmetry-group-cipher-bsidessf-2026)
- **Goldwasser-Micali replication oracle:** GM encrypts one bit per ciphertext; replaying a single ciphertext value N times as an N-bit key forces all-zero or all-one key, distinguishable via hash oracle. 128 queries recover full AES key. See [exotic-crypto.md](exotic-crypto.md#goldwasser-micali-ciphertext-replication-oracle-bsidessf-2026)
- **DSA nonce reuse:** Same r in two DSA signatures leaks private key via same formula as ECDSA nonce reuse. See [ecc-attacks.md](ecc-attacks.md#dsa-nonce-reuse-for-private-key-recovery-volgactf-2016).
- **DSA limited k brute force:** When nonce `k` is small (e.g., 20-bit), brute-force all `k` values and check which yields the known `r`. See [ecc-attacks.md](ecc-attacks.md#dsa-limited-k-value-brute-force-asis-ctf-finals-2016).
- **ECC shared prime GCD:** Multiple ECC curves sharing a prime factor in their modulus; `gcd(n1, n2)` reveals the shared prime. See [ecc-attacks.md](ecc-attacks.md#ecc-shared-prime-factor-via-gcd-asis-ctf-finals-2016).
- **DSA key recovery via MD5 collision on k-generation:** When nonce `k` derives from `MD5(prefix+counter)`, use `fastcoll` to produce MD5 prefix collision forcing nonce reuse, then standard private key recovery. See [ecc-attacks.md](ecc-attacks.md#dsa-key-recovery-via-md5-collision-on-k-generation-confidence-ctf-2017).
- **BB-84 QKD MITM:** Simulated BB-84 without authenticated classical channels allows full MITM -- independently negotiate keys with both parties, force constant value to one side. See [exotic-crypto-2.md](exotic-crypto-2.md#bb-84-quantum-key-distribution-mitm-attack-plaidctf-2017).

See [ecc-attacks.md](ecc-attacks.md), [advanced-math.md](advanced-math.md), and [exotic-crypto.md](exotic-crypto.md) for full code examples.


## Lattice / LWE Attacks

- **Quick triage:** If the challenge gives modular linear equations plus a promise that the hidden quantity is small, sparse, biased, or only partially leaked, treat it as a lattice candidate first. See [lattice-and-lwe.md](lattice-and-lwe.md#quick-triage-is-this-a-lattice-problem).
- **LLL / BKZ / Babai:** Start with LLL, move to BKZ when LLL almost works, and use Babai after reduction for approximate CVP. See [lattice-and-lwe.md](lattice-and-lwe.md#core-tools-lll-bkz-babai-cvp-svp-asis-ctf-finals-2015-ctfzone-2017).
- **HNP from partial nonce leakage:** Partial or biased ECDSA/Schnorr nonces often reduce to Hidden Number Problem lattices; normalize equations, isolate bounded error, reduce, then brute-force the last few bits if needed. See [lattice-and-lwe.md](lattice-and-lwe.md#hidden-number-problem-hnp-partial-nonce--biased-nonce-nullcon-hackim-2020-ledger-donjon-ctf-2020).
- **Truncated LCG state recovery:** High-bit or low-bit leakage from affine recurrences is often just HNP in disguise; write each state as `observed * 2^t + hidden` and solve for the small hidden corrections. See [lattice-and-lwe.md](lattice-and-lwe.md#lcg-and-truncated-output-as-a-lattice-problem-x-mas-ctf-2018-fwordctf-2020).
- **LWE via CVP (Babai):** Construct lattice from `[q*I | 0; A^T | I]`, use fpylll CVP.babai to find closest vector, project to ternary {-1,0,1}. Watch for endianness mismatches between server description and actual encoding.
- **Ring-LWE / Module-LWE recognition:** Polynomial or negacyclic structure often looks scary but many CTFs weaken it with tiny coefficients, buggy representations, or enough leakage to flatten back into plain LWE. See [lattice-and-lwe.md](lattice-and-lwe.md#ring-lwe--module-lwe-recognition-notes-plaidctf-2016-dicectf-2022).
- **Orthogonal lattices:** Hidden subset or hidden subspace problems may need you to recover an orthogonal lattice first, then reconstruct the actual binary or short basis from its complement. See [lattice-and-lwe.md](lattice-and-lwe.md#orthogonal-lattices-hssp--ahssp-style-recovery-zer0pts-ctf-2022).
- **LLL for approximate GCD:** Short vector in lattice reveals hidden factors
- **Subset sum / knapsack:** Binary knapsack and low-density subset-sum instances are still classic lattice territory; build the standard basis and look for a reduced row with a zero final coordinate. See [lattice-and-lwe.md](lattice-and-lwe.md#subset-sum--knapsack-via-lattice-reduction-hitcon-ctf-2017-backdoorctf-2023).
- **Multi-layer challenges:** Geometry → subspace recovery → LWE → AES-GCM decryption chain

See [advanced-math.md](advanced-math.md) for worked LWE solving code and [lattice-and-lwe.md](lattice-and-lwe.md) for attack selection, embeddings, and failure-mode triage.


## ZKP & Constraint Solving

- **ZKP cheating:** For impossible problems (3-coloring K4), find hash collisions or predict PRNG salts
- **Graph 3-coloring:** `nx.coloring.greedy_color(G, strategy='saturation_largest_first')`
- **Z3 solver:** BitVec for bit-level, Int for arbitrary precision; BPF/SECCOMP filter solving
- **Garbled circuits (free XOR):** XOR three truth table entries to recover global delta
- **Bigram substitution:** OR-Tools CP-SAT with automaton constraint for known plaintext structure
- **Trigram decomposition:** Positions mod n form independent monoalphabetic ciphers
- **Shamir SSS (deterministic coefficients):** One share + seeded RNG = univariate equation in secret
- **Race condition (TOCTOU):** Synchronized concurrent requests bypass `counter < N` checks
- **Groth16 broken setup (delta==gamma):** Trivially forge: A=alpha, B=beta, C=-vk_x. Always check verifier constants first
- **Groth16 proof replay:** Unconstrained nullifier + no tracking = infinite replays from setup tx
- **DV-SNARG forgery:** With verifier oracle access, learn secret v values from unconstrained pairs, forge via CRS entry cancellation
- **Shamir SSS reused polynomial coefficients:** When same random coefficients are used for every secret byte, subtracting shares cancels all randomness, leaving only plaintext differences. See [zkp-and-advanced.md](zkp-and-advanced.md#shamir-secret-sharing-with-reused-polynomial-coefficients-polictf-2017).

See [zkp-and-advanced.md](zkp-and-advanced.md) for full code examples and solver patterns.


