# XOR Cipher Analysis

## Single Byte XOR
```python
# Brute force all 256 keys
for key in range(256):
    decrypted = bytes([b ^ key for b in ciphertext])
    if b'flag' in decrypted or b'CTF' in decrypted:
        print(f"Key: {key}, Text: {decrypted}")
```

## Repeating Key XOR
```python
# Find key length first (Kasiski/Friedman test)
# Then treat as multiple single-byte XORs

# Key length detection
def find_key_length(ciphertext, max_len=40):
    scores = []
    for kl in range(2, max_len):
        chunks = [ciphertext[i:i+kl] for i in range(0, len(ciphertext), kl)]
        score = sum(hamming_distance(chunks[i], chunks[i+1]) for i in range(min(4, len(chunks)-1)))
        scores.append((kl, score/min(4, len(chunks)-1)))
    return sorted(scores, key=lambda x: x[1])[:5]

# After finding key length, solve each position as single-byte XOR
```

## XOR Properties
```
A XOR A = 0
A XOR 0 = A
A XOR B = C → C XOR B = A
A XOR B = C → C XOR A = B
```

## Known Plaintext XOR
```python
# If you know part of plaintext
key = bytes([ciphertext[i] ^ known[i] for i in range(len(known))])
```

## XOR with Key Recovery
```python
# If you have plaintext and ciphertext
key = bytes([c[i] ^ p[i] for i in range(len(p))])
# Repeated key will appear in multiple positions
```

## Common XOR Patterns
```python
# XOR with constant
encrypted[i] = plaintext[i] ^ KEY

# XOR with position
encrypted[i] = plaintext[i] ^ (i % KEY_LENGTH)

# XOR with previous block (CFB-like)
encrypted[i] = plaintext[i] ^ encrypted[i-1]
```

## Tools
```
xortool           # XOR analysis
CyberChef         # Multi-format
```
