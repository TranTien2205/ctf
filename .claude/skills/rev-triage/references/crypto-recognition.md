# Crypto Algorithm Recognition in Binaries

## Common Constant Signatures

### AES Constants
```
S-box first bytes: 63 7c 77 7b f2 6b 6f c5
Rcon values: 01 02 04 08 10 20 40 80 1b 36
```

### MD5 Constants
```
Initial hash values: 67452301 efcdab89 98badcfe 10325476
```

### SHA-1 Constants
```
Initial hash values: 67452301 EFCDAB89 98BADCFE 10325476 C3D2E1F0
```

### SHA-256 Constants
```
Initial hash values: 6a09e667 bb67ae85 3c6ef372 a54ff53a
K constants start: 428a2f98 71374491 b5c0fbcf e9b5dba5
```

### RC4 Indicators
```
- 256-byte S-box initialization loop (for i in 0..255: S[i] = i)
- Swap-based key scheduling algorithm (KSA)
- Simple XOR in pseudo-random generation (PRGA)
```

### DES Constants
```
Initial Permutation table, S-box tables (8 S-boxes of 64 entries each)
```

### Base64 Alphabet
```
"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
```

## Tool-Assisted Detection

### findcrypt (IDA Plugin)
```
# Scans binary for known crypto constant signatures
# Install: IDA plugins folder, then Edit > Plugins > FindCrypt
```

### Ghidra Crypto Signature Search
```
# Search > For Scalars, input known constant (e.g., 0x67452301 for MD5/SHA1)
# Or use CryptoAnalyzer/similar Ghidra scripts
```

### YARA Rules for Crypto Detection
```bash
yara crypto_signatures.yar ./binary
# Use community rule sets like "capa" rules for crypto detection
capa ./binary   # Detects capabilities including crypto usage
```

## Identifying Algorithm from Code Structure
```
Loop with 64 rounds + specific shift amounts    → MD5
Loop with 80 rounds                              → SHA-1
Loop with 64 rounds + more complex message schedule → SHA-256
256-byte array shuffle then XOR stream           → RC4
4x4 byte matrix operations, ShiftRows/SubBytes   → AES
Feistel network structure, 16 rounds             → DES
```

## Custom/Weak Crypto Recognition (Common in CTF)
```
Simple XOR with static key                       → XOR cipher
Caesar/ROT shift patterns                         → Classical substitution
Linear Congruential Generator (LCG) patterns      → Predictable "random" (seed recoverable)
Custom S-box but standard structure               → Modified AES/DES variant
```

## Extracting Keys/IVs from Binary
```bash
# Static keys often embedded as byte arrays near crypto function calls
objdump -s -j .rodata ./binary | head -50
strings -t x ./binary | grep -A2 -B2 "key\|iv\|secret"

# Dynamic extraction via debugger breakpoint at crypto function entry
gdb ./binary
(gdb) break *0x<crypto_func_addr>
(gdb) run
(gdb) x/16xb $rdi    # inspect key buffer argument
```

## Workflow
```
1. Search binary for known constant signatures (findcrypt/capa/manual grep)
2. Identify exact algorithm from constants + code structure
3. Locate where key/IV is set (often right before encrypt/decrypt call)
4. Extract key/IV via static analysis or dynamic breakpoint
5. Reimplement or use library (PyCryptodome) to decrypt with recovered key
```
