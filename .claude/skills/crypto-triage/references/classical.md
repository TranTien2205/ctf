# Classical Cipher Attacks

## Caesar Cipher (Shift Cipher)
```python
def caesar_bruteforce(ciphertext):
    for shift in range(26):
        result = ''.join(
            chr((ord(c) - ord('a') - shift) % 26 + ord('a')) if c.isalpha() else c
            for c in ciphertext.lower()
        )
        print(f"Shift {shift}: {result}")
```

## ROT13
```python
import codecs
plaintext = codecs.decode(ciphertext, 'rot13')
```

## Vigenere Cipher

### Kasiski Examination (Find Key Length)
```python
from collections import Counter

def find_repeated_sequences(text, seq_len=3):
    sequences = {}
    for i in range(len(text) - seq_len):
        seq = text[i:i+seq_len]
        if seq in sequences:
            sequences[seq].append(i)
        else:
            sequences[seq] = [i]
    return {k: v for k, v in sequences.items() if len(v) > 1}

# Distances between repeats often share common factors = key length
```

### Vigenere Decrypt (Known Key)
```python
def vigenere_decrypt(ciphertext, key):
    result = []
    key = key.lower()
    key_idx = 0
    for c in ciphertext:
        if c.isalpha():
            shift = ord(key[key_idx % len(key)]) - ord('a')
            decrypted = chr((ord(c.lower()) - ord('a') - shift) % 26 + ord('a'))
            result.append(decrypted.upper() if c.isupper() else decrypted)
            key_idx += 1
        else:
            result.append(c)
    return ''.join(result)
```

### Frequency Analysis for Unknown Key
```python
# Use chi-squared test against English letter frequency
# for each possible key length, split ciphertext into columns,
# treat each column as Caesar cipher, solve independently
```

## Substitution Cipher (Monoalphabetic)
```python
# Frequency analysis approach
from collections import Counter
freq = Counter(ciphertext.lower())
# Most common English letters: E T A O I N S H R D L U
# Map most frequent ciphertext letters to most frequent English letters as starting guess

# Automated: quipqiup.com style solver, or use simulated annealing
```

## Automated Solvers
```
quipqiup.com               # Online substitution cipher solver
CyberChef "Magic" wand      # Auto-detects many classical ciphers
dcode.fr                    # Comprehensive classical cipher solvers
```

## Rail Fence Cipher
```python
def rail_fence_decrypt(ciphertext, rails):
    fence = [[] for _ in range(rails)]
    rail, direction = 0, 1
    positions = []
    for _ in ciphertext:
        positions.append(rail)
        rail += direction
        if rail == rails - 1 or rail == 0:
            direction *= -1

    idx = 0
    result = [None] * len(ciphertext)
    for r in range(rails):
        for i, pos in enumerate(positions):
            if pos == r:
                result[i] = ciphertext[idx]
                idx += 1
    return ''.join(result)
```

## Playfair Cipher
```python
# Requires 5x5 key square (I/J combined)
# Decrypt in digraphs (pairs), reverse the row/column shift rules
# Manual approach or use pycipher library
from pycipher import Playfair
p = Playfair('KEYWORD')
plaintext = p.decipher(ciphertext)
```

## Atbash Cipher
```python
def atbash(text):
    return ''.join(
        chr(ord('z') - (ord(c) - ord('a'))) if c.isalpha() else c
        for c in text.lower()
    )
```

## Base Encoding Chains (often combined with classical ciphers in CTF)
```bash
# Try decoding stacked encodings
echo "CIPHERTEXT" | base64 -d | base32 -d
# CyberChef "Magic" can auto-detect encoding chains
```

## Tools
```
CyberChef          # Swiss-army-knife, has Magic auto-detect
dcode.fr            # Comprehensive cipher identification/solving
pycipher            # Python library for classical ciphers
quipqiup.com        # Substitution cipher solver
```
