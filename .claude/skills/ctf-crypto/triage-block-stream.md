# Block and stream cipher attacks

Mode-level weaknesses: ECB structure, CBC malleability and padding, CTR nonce
reuse, keystream bias. Depth in `modern-ciphers*.md` and `stream-ciphers.md`.

Moved out of `SKILL.md` so the router stays thin. Content is unchanged.

---

## Modern Cipher Attacks

- **AES-ECB:** Block shuffling, byte-at-a-time chosen-plaintext suffix recovery (256 queries per byte, tool: FeatherDuster `ecb_cpa_decrypt`); image ECB preserves visual patterns. ECB cut-and-paste: splice ciphertext blocks to forge JSON fields (e.g., `is_admin: true`). See [modern-ciphers-2.md](modern-ciphers-2.md#aes-ecb-byte-at-a-time-chosen-plaintext-abctf-2016).
- **AES-CBC:** Bit flipping to change plaintext; padding oracle for decryption without key. IV bit-flip: flip specific bits in the IV to change first plaintext block (requires no MAC). See [modern-ciphers-2.md](modern-ciphers-2.md#aes-cbc-iv-bit-flip-authentication-bypass-google-ctf-2016).
- **CBC IV forgery + block truncation:** XOR IV bytes to change decrypted block 0; strip trailing ciphertext blocks (no length integrity in CBC). Forges authenticated tokens when MAC is embedded in the ciphertext. See [modern-ciphers-2.md](modern-ciphers-3.md#cbc-iv-forgery--block-truncation-for-authentication-bypass-0ctf-2017).
- **Padding oracle to CBC bitflip RCE:** Chain padding oracle (recover plaintext) with CBC bitflipping (inject shell metacharacters) for command injection via encrypted parameters. See [modern-ciphers-2.md](modern-ciphers-3.md#padding-oracle-to-cbc-bitflip-command-injection-bsidessf-2017).
- **AES-CFB-8:** Static IV with 8-bit feedback allows state reconstruction after 16 known bytes
- **CBC-MAC/OFB-MAC:** XOR keystream for signature forgery: `new_sig = old_sig XOR block_diff`
- **S-box collisions:** Non-permutation S-box (`len(set(sbox)) < 256`) enables 4,097-query key recovery
- **GF(2) elimination:** Linear hash functions (XOR + rotations) solved via Gaussian elimination over GF(2)
- **Padding oracle:** Byte-by-byte decryption by modifying previous block and testing padding validity
- **LFSR stream ciphers:** Berlekamp-Massey recovers feedback polynomial from 2L keystream bits; correlation attack breaks combined generators with biased combining functions
- **Galois LFSR tap recovery:** XOR known file header (PNG/PDF/ZIP) with ciphertext to get keystream; split into N-bit windows, compute `(state >> 1) XOR next_state` for LSB=1 transitions to directly recover tap mask. Autocorrelation sliding finds correct length. See [stream-ciphers.md](stream-ciphers.md#galois-lfsr-tap-recovery-via-autocorrelation-bsidessf-2026).
- **OFB with invertible RNG:** Known plaintext in any block leaks RNG state; if state transition is bijective, run RNG backwards to decrypt all blocks. See [modern-ciphers-2.md](modern-ciphers-2.md#ofb-mode-with-invertible-rng-backward-decryption-bsidessf-2026).
- **Weak key derivation (public key hash XOR):** AES key derived from `SHA256(public_key) XOR seed` is fully recoverable without private key; "hybrid" RSA+AES provides no security. See [modern-ciphers-2.md](modern-ciphers-2.md#weak-key-derivation-via-public-key-hash-xor-bsidessf-2026).
- **HMAC-CRC linearity:** CRC is linear over GF(2), so HMAC-CRC key is recoverable from a single message-MAC pair via polynomial arithmetic. See [modern-ciphers-2.md](modern-ciphers-2.md#hmac-crc-linearity-attack-boston-key-party-2016).
- **DES weak keys in OFB:** 4 DES weak keys make encryption self-inverse; OFB keystream cycles with period 2, reducing to 16-byte repeating XOR. See [modern-ciphers-2.md](modern-ciphers-2.md#des-weak-keys-in-ofb-mode-boston-key-party-2016).
- **Square attack (reduced-round AES):** 4-round AES broken by integral cryptanalysis: 256-plaintext lambda set, guess last round key bytes via XOR-sum = 0 distinguisher. See [modern-ciphers-2.md](modern-ciphers-2.md#square-attack-on-reduced-round-aes-0ctf-2016).
- **AES-GCM nonce reuse (forbidden attack):** Same nonce = CTR keystream reuse + GHASH authentication key recovery via polynomial factoring over GF(2^128). Tool: `nonce-disrespect`. See [modern-ciphers.md](modern-ciphers.md#aes-gcm-nonce-reuse--forbidden-attack).
- **SRP protocol bypass:** Send `A = 0` or `A = n` to force shared secret to 0, bypassing password verification entirely. See [modern-ciphers-2.md](modern-ciphers-2.md#srp-secure-remote-password-protocol-bypass-via-modular-arithmetic-asis-ctf-finals-2016).
- **Modified AES S-Box brute force:** Custom S-Box with only 16 unique outputs reduces key entropy; brute-force feasible key bytes per round. See [modern-ciphers-2.md](modern-ciphers-2.md#modified-aes-s-box-brute-force-recovery-h4ckit-ctf-2016).
- **Rabin LSB parity oracle:** Rabin ciphertext `c = m^2 mod n` with LSB oracle enables binary search plaintext recovery in `log2(n)` queries via multiplicative homomorphism (`c * 4 mod n` doubles plaintext). See [modern-ciphers-2.md](modern-ciphers-2.md#rabin-cryptosystem-lsb-parity-oracle-plaidctf-2016).
- **Noisy RSA LSB oracle error correction:** When LSB oracle has sporadic errors, run standard attack then inspect output charset. Flip oracle results at error positions to correct remaining decryption. See [modern-ciphers-2.md](modern-ciphers-3.md#noisy-rsa-lsb-oracle-with-post-hoc-error-correction-sharifctf-7-2016).
- **PBKDF2 pre-hash bypass:** HMAC pre-hashes keys > 64 bytes (SHA-1/SHA-256 block size). Login with `SHA1(password)` instead of `password` when original exceeds 64 bytes. See [modern-ciphers-2.md](modern-ciphers-2.md#pbkdf2-pre-hash-bypass-for-long-passwords-backdoorctf-2016).
- **MD5 multi-collision (fastcol):** Chain `fastcol` runs to produce 2^k files with identical MD5. Merkle-Damgard composition: collisions propagate through appended suffixes. See [modern-ciphers-2.md](modern-ciphers-2.md#md5-multi-collision-via-fastcol-backdoorctf-2016).
- **Custom hash state reversal:** When iterative hash leaks intermediate states, isolate per-block hash values by inverting the state update equation, then brute-force each 4-byte block independently. See [modern-ciphers-2.md](modern-ciphers-3.md#custom-hash-state-reversal-via-known-intermediates-backdoorctf-2016).
- **CRC32 brute-force (small payloads):** ZIP CRC32 headers are unencrypted; brute-force content of small files (≤ 6 bytes) by checking all printable strings against stored CRC32. See [modern-ciphers-2.md](modern-ciphers-3.md#crc32-brute-force-for-small-payloads-backdoorctf-2016).
- **Custom MAC forgery via XOR block cancellation:** When MAC key stream repeats periodically, craft three queries where filler blocks cancel via XOR, forging any target command's MAC. See [modern-ciphers-2.md](modern-ciphers-3.md#custom-mac-forgery-via-xor-block-cancellation-with-key-rotation-plaidctf-2018).
- **HMAC key recovery (XOR + addition arithmetic):** Flawed HMAC using `sha256((key XOR msg) + msg)` leaks key bits: `msg=0` gives `sha256(key)`, `msg=2^i` matches iff key bit `i` is set. See [modern-ciphers-2.md](modern-ciphers-3.md#bit-by-bit-hmac-key-recovery-via-xor-plus-addition-arithmetic-midnight-sun-ctf-2018).
- **AES-CBC ciphertext forging (error-message oracle):** Server leaks decrypted bytes in error messages; send zero blocks to learn intermediate state, XOR with desired plaintext to forge ciphertext block-by-block. See [modern-ciphers.md](modern-ciphers.md#aes-cbc-ciphertext-forging-via-error-message-decryption-oracle-nuit-du-hack-ctf-2018).

See [modern-ciphers.md](modern-ciphers.md) and [modern-ciphers-2.md](modern-ciphers-2.md) for full code examples.


## Modern Cipher Attacks (Additional)

- **Affine over composite modulus:** `c = A*x+b (mod M)`, M composite (e.g., 65=5*13). Chosen-plaintext recovery via one-hot vectors, CRT inversion per prime factor. See [modern-ciphers.md](modern-ciphers.md#affine-cipher-over-composite-modulus-nullcon-2026).
- **Custom linear MAC forgery:** XOR-based signature linear in secret blocks. Recover secrets from ~5 known pairs, forge for target. See [modern-ciphers.md](modern-ciphers.md#custom-linear-mac-forgery-nullcon-2026).
- **Manger oracle (RSA threshold):** RSA multiplicative + binary search on `m*s < 2^128`. ~128 queries to recover AES key.
- **AES key recovery via byte-by-byte zeroing oracle:** Integer overflow in key slot indexing allows selective byte zeroing; brute-force one byte at a time (256 per byte, 4096 total). See [modern-ciphers.md](modern-ciphers.md#aes-key-recovery-via-byte-by-byte-zeroing-oracle-confidence-ctf-2017).


## CBC Padding Oracle Attack

Server reveals valid/invalid padding → decrypt any CBC ciphertext without key. ~4096 queries per 16-byte block. Use PadBuster or `padding-oracle` Python library. See [modern-ciphers.md](modern-ciphers.md#cbc-padding-oracle-attack).


## Compression Oracle (CRIME-Style)

Compression before encryption leaks plaintext via ciphertext length changes. Send chosen plaintexts; matching n-grams compress shorter. Same class as CRIME/BREACH. See [modern-ciphers-2.md](modern-ciphers-2.md#compression-oracle--crime-style-attack-bctf-2015).


## RC4 Second-Byte Bias

RC4's second output byte is biased toward `0x00` (probability 1/128 vs 1/256). Distinguishes RC4 from random with ~2048 samples. See [stream-ciphers.md](stream-ciphers.md#rc4-second-byte-bias-distinguisher-hackover-ctf-2015).


## SPN S-box Intersection Attack

Divide-and-conquer SPN key recovery: attack each S-box position independently, intersect valid key candidates across multiple plaintext-ciphertext pairs. Reduces exponential key space to independent sub-key searches. See [modern-ciphers-2.md](modern-ciphers-3.md#spn-cipher-partial-key-recovery-via-s-box-intersection-sharifctf-7-2016).


