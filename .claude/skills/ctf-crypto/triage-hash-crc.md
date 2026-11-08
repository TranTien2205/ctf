# Hashes, checksums and forgery

Length extension, collisions, and the linear structure of CRC.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Hash Length Extension Attack

Exploits Merkle-Damgard hashes (`hash(SECRET || user_data)`) — append arbitrary data and compute valid hash without knowing the secret. Use `hashpump` or `hashpumpy`. See [modern-ciphers-2.md](modern-ciphers-2.md#hash-length-extension-attack-plaidctf-2014).


## Birthday Attack / Meet-in-the-Middle

n-bit hash collision in ~2^(n/2) attempts. Meet-in-the-middle breaks double encryption in O(2^k) instead of O(2^(2k)). See [modern-ciphers.md](modern-ciphers.md#birthday-attack--meet-in-the-middle).

- **Sponge hash MITM collision:** When sponge rate < state size, uncontrolled state bytes enable MITM — precompute forward encryptions keyed on uncontrolled bytes, search backward for matches. Reduces 2^48 to 2^24. See [modern-ciphers-2.md](modern-ciphers-3.md#sponge-hash-collision-via-meet-in-the-middle-on-partial-state-bkp-2017).


## Introspective CRC via GF(2) Linear Algebra

Self-referential CRC: find ASCII string whose CRC equals itself. CRC is linear over GF(2), so the constraint becomes a solvable linear system. Free variables chosen for printable ASCII range. See [advanced-math.md](advanced-math.md#introspective-crc-via-gf2-linear-algebra-google-ctf-2017).


## CRC32 Collision-Based Signature Forgery (iCTF 2013)

CRC32 is linear — append 4 chosen bytes to force any target CRC32, forging `CRC32(msg || secret)` signatures without the secret. See [modern-ciphers.md](modern-ciphers.md#crc32-collision-based-signature-forgery-ictf-2013).


