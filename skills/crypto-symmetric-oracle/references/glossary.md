# Glossary — the vocabulary used across this corpus

| Term | Meaning here |
|---|---|
| oracle | any endpoint that answers a question about ciphertext/plaintext/tag |
| distinguisher | the response channel (status/body/length/timing) that separates the oracle's two answers |
| ECB | electronic codebook — each block independent, deterministic |
| CBC | cipher-block chaining — P_i = D(C_i) XOR C_{i-1} |
| CTR | counter mode — XOR keystream; nonce reuse = keystream reuse |
| GCM | Galois/counter — CTR + GHASH authentication |
| PKCS#7 | block padding to a multiple; 'valid pad' is the oracle's question |
| malleability | ciphertext edits produce predictable plaintext edits |
| crib | a guessed plaintext word slid across P1 XOR P2 |
| glue padding | the MD pad bytes between original and appended data in length extension |
| GHASH / H | GCM's authentication polynomial and its key |
| byte-at-a-time | ECB decryption via one-byte-per-block brute force |
| cut-and-paste | splicing ECB blocks between tokens |
| Vaudenay attack | the CBC padding oracle decryption method |
| false positive (pad) | a guess that validates as \\x01 when the real pad is longer |
| block alignment | where the attacker-controlled bytes begin relative to cipher blocks |
| deterministic | same input → same output (ECB or fixed IV) |
| authenticated-before-decrypt | a tag verified before decryption — closes all malleability oracles |
| MAC | message authentication code/tag |
| HMAC | keyed hash MAC — immune to length extension |
| Merkle-Damgard | the iterated-hash structure (sha1/sha256/md5) that leaks state |
| keystream | the pseudorandom XOR stream in CTR/stream modes |
| KDF | key derivation function — how the key is produced |
| forgery | a tag or token the attacker produces without the key |
| verification oracle | an endpoint that only answers valid/invalid |
