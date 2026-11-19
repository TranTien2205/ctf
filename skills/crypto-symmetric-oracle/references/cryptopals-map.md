# Cryptopals map — this class, set by set

The class IS most of cryptopals sets 1-3. The map is worth knowing because
CTF authors lift these exercises almost verbatim.

## Set 1 — basics

| Challenge | Attack here |
|---|---|
| 1-3 single-byte XOR | `single-byte-xor.md` |
| 6 repeating-key XOR | `single-byte-xor.md` (keysize via Hamming) |
| 7 AES-ECB decrypt with key | key-path (decrypt directly) |
| 8 detect ECB in a batch | `ecb-detection.md` |

## Set 2 — block crypto

| Challenge | Attack here |
|---|---|
| 9 PKCS#7 pad | boundary math |
| 10 CBC round-trip | mechanism |
| 11 ECB/CBC detection oracle | `detection.md` |
| 12 byte-at-a-time ECB | `ecb-byte-at-a-time.md` |
| 13 cut-and-paste profile | `ecb-cut-and-paste.md` |
| 14 byte-at-a-time with random prefix | `block-alignment.md` |
| 15 pad validation | boundary |
| 16 CBC bit-flip 'admin=true' | `cbc-bitflip.md` |

## Set 3 — block/stream crypto

| Challenge | Attack here |
|---|---|
| 17 CBC padding oracle | `cbc-padding-oracle.md` |
| 18 CTR round-trip | mechanism |
| 19-20 fixed-nonce CTR | `ctr-nonce-reuse.md` |
| 21 MT19937 | `../crypto-prng/` |
| 23 clone MT | `../crypto-prng/` |
| 24 MT19937 keystream | `ctr-nonce-reuse.md` + prng |

## Using the map

A challenge that smells like 'encrypt a profile' is #13-shaped; a 'decrypt
endpoint that errors on padding' is #17. The mechanism is identical — only
the transport differs.
