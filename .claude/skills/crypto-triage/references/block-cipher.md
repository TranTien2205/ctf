# Block Cipher Attacks (AES/DES)

## ECB Mode Attacks

### Detection
```python
# Identical plaintext blocks → identical ciphertext blocks
blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
if len(blocks) != len(set(blocks)):
    print("ECB mode detected!")
```

### Byte-at-a-Time
```python
# If server encrypts user_input + secret
# Control block boundary to reveal secret byte by byte
```

### Block Rearrangement
```python
# Swap blocks to change meaning
# e.g., admin=false → admin=true
```

## CBC Mode Attacks

### Padding Oracle
```python
# If server returns different errors for bad padding vs bad data
# Use poc.py or padbuster

# Manual decryption
def xor_blocks(a, b):
    return bytes([x ^ y for x, y in zip(a, b)])

# For each byte position (from last to first):
# Modify IV to produce desired padding
# Observe server response
```

### IV Manipulation
```python
# CBC: Decrypt(c, iv) = AES_Decrypt(c) XOR iv
# Changing iv[i] flips plaintext[i]
# Flip bits in IV to change plaintext
```

### Bit-Flipping Attack
```python
# C1 = Enc(P1 XOR IV)
# To change P1[i] to desired:
# new_iv[i] = iv[i] XOR original_plaintext[i] XOR desired_plaintext[i]
```

## CTR Mode Attacks

### Nonce Reuse
```python
# c1 = m1 XOR keystream
# c2 = m2 XOR keystream
# c1 XOR c2 = m1 XOR m2
# If m1 known: keystream = c1 XOR m1
# Then: m2 = c2 XOR keystream
```

### Known Plaintext
```python
# keystream = ciphertext XOR plaintext
# Decrypt other messages with same nonce
```

## Tools
```
CyberChef         # Multi-format crypto
hashcat            # Hash cracking
John the Ripper    # Password cracking
```
