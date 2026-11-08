# Hash Attacks

## Identifying Hash Type by Length/Format
```
32 hex chars (128 bit)   → MD5
40 hex chars (160 bit)   → SHA-1
64 hex chars (256 bit)   → SHA-256
96 hex chars (384 bit)   → SHA-384
128 hex chars (512 bit)  → SHA-512
$1$...                   → MD5 crypt (Unix)
$2a$/$2b$/$2y$...        → bcrypt
$6$...                   → SHA-512 crypt (Unix)
$argon2...                → Argon2
```

### Automated Identification
```bash
hashid <hash>
hash-identifier
```

## Cracking with Hashcat
```bash
# MD5
hashcat -m 0 hash.txt rockyou.txt

# SHA-1
hashcat -m 100 hash.txt rockyou.txt

# SHA-256
hashcat -m 1400 hash.txt rockyou.txt

# bcrypt
hashcat -m 3200 hash.txt rockyou.txt

# NTLM
hashcat -m 1000 hash.txt rockyou.txt

# With rules for mutation
hashcat -m 0 hash.txt rockyou.txt -r rules/best64.rule
```

## Cracking with John the Ripper
```bash
john --wordlist=rockyou.txt hash.txt
john --format=raw-md5 hash.txt
john --show hash.txt
```

## Hash Length Extension Attack (MD5/SHA1/SHA256 - Merkle-Damgard construction)
```bash
# If server computes: hash(secret + known_data) and you can append data
hashpump  # or use python hlextend library

python3 -c "
import hlextend
h = hlextend.new('sha1')
new_hash = h.extend(b'&admin=true', b'known_data', secret_len_guess, original_hash)
print(new_hash, h.hexdigest())
"
```

## Precomputed / Rainbow Table Lookups
```bash
# Online lookup for common/unsalted hashes
# crackstation.net, hashes.com

# Local rainbow table with hashcat
hashcat -m 0 hash.txt --rainbow-table
```

## Salted Hash Cracking
```bash
# Format: hash:salt or salt:hash - identify with hashid
hashcat -m 20 hash:salt rockyou.txt   # md5($pass.$salt)
hashcat -m 10 hash:salt rockyou.txt   # md5($salt.$pass)
```

## HMAC Attacks
```python
# If HMAC key is weak/guessable, brute force
import hmac
import hashlib

for key in wordlist:
    computed = hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()
    if computed == target_hmac:
        print(f"Key found: {key}")
        break
```

## Common Weak Hash Patterns in CTF
```
- Hash of sequential/predictable input (timestamp, incrementing ID)
- Truncated hash (only first N chars shown - reduces brute force space significantly)
- Custom "hash" that's actually reversible (e.g., simple XOR disguised as hash)
```

## GPU Cracking Setup Tips
```bash
hashcat -b               # Benchmark to verify GPU is detected
hashcat -I                # List OpenCL/CUDA devices
hashcat -m <mode> hash.txt wordlist.txt -O -w 3   # -O optimized, -w 3 high workload
```

## Tools
```
hashcat            # GPU-accelerated cracking
John the Ripper    # CPU cracking, many format supports
hashid             # Hash type identification
hlextend           # Hash length extension attacks
CyberChef           # Quick hash computation/comparison
```
