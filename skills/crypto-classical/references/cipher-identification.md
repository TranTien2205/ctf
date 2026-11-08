# Identifying the cipher from statistics

## First five minutes

| Measure | Command | Reads as |
|---|---|---|
| alphabet | look at chars | all-A-Z = classical; mixed b64 = encoding not cipher |
| top letters | Counter | E/T/A spikes in-place = transposition or nothing done |
| IC (index of coincidence) | ~0.066 vs ~0.038 | 0.066 monoalpha (Caesar/substitution); 0.038 polyalpha (Vigenere) |
| repeated chunks | every N chars | Vigenere period = gcd of repeat spacings (Kasiski) |

## Family cheat-table

| Cipher | Tell | Solve |
|---|---|---|
| Caesar | IC ~0.066, letter counts shifted uniformly | 25 shifts, grep English |
| Atbash | reversed alphabet | A<->Z swap, instant |
| Substitution | IC ~0.066, spikes present, wrong letters | frequency map + quipqiup/dcode |
| Vigenere | IC ~0.038, periodic repeats | period from Kasiski, then per-column Caesar |
| Transposition | plaintext letter frequencies intact, text garbled | rail-fence depths, columnar widths |
| Playfair | even length, no J, bigram structure | playfair solver |
| Rail-fence | same frequency as plaintext | try depths 2..len/3 |
| XOR single-byte | any alphabet, printable key space | try 256 keys, score English |

## When it is not classical

b64/hex/base85-looking text, `=` padding, or structured blobs are encodings —
route to misc-encoding-carrier. Random-looking bytes with a key phrase are
modern crypto — route back to crypto-triage. Honest classification beats a
forced solve.

## Key-word habits

Challenge authors key Vigenere/Playfair with words FROM the challenge:
title, names, the ciphertext's own theme. Try those first; Kasiski is the
fallback, not the opener.
